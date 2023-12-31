#!/usr/bin/env python
if __name__ != '__main__': raise Exception("Do not import me!")  # noqa: E701

import chainer
import logging
import numpy as np
import os

from chainercv import transforms as tr
from chainercv.links.model.ssd import multibox_loss
from cvdatasets import utils as data_utils
from cvdatasets.dataset.image import Size
from cvmodelz.models import ModelFactory
from matplotlib import pyplot as plt
from pathlib import Path
from tqdm import tqdm

from scanner import parser

try:
	from moth_detector.core import models as det_models
	from moth_detector.core import detectors
	from moth_detector.core.dataset.bbox_dataset import BBoxDataset

	from moth_classifier.core import classifier as clf_module
except ImportError as e:
	print(f"Could not import detection and classifierion modules: {e}.\n"\
		"Consider setting the python path (PYTHONPATH) accordingly!")
	raise

def load_blob_detector(size=(1280, 1920)):
	logging.info("Creating a blob detector")
	model_cls = det_models.get("shallow")
	model = model_cls(input_size=Size(size))

	detector = detectors.shallow.Detector(
		model=model,
		nms_thresh=0.45,
		score_thresh=0.1,
		max_boxes=128
	)

	return detector

def load_detector(args):
	if args.detector == "blob_detector":
		return load_blob_detector(), True

	weights = Path(args.detector)
	opts = parser.load_yaml(weights.parent / "meta/args.yml")

	logging.info(f"Loading detector from {weights}")
	params = detectors.kwargs(opts)

	detector_cls = params["classifier_cls"]
	detector_kwargs = params["classifier_kwargs"]
	model_kwargs = params["model_kwargs"]

	model_cls = det_models.get(opts.model_type)
	input_size = Size(opts.input_size)

	model = model_cls(input_size=input_size, **model_kwargs)
	detector = detector_cls(model=model, loss_func=multibox_loss, **detector_kwargs)
	detector.load(weights, n_classes=None, strict=True, finetune=False)

	return detector, False


def infer_from_weights(weights, model, prefix="model"):
	content = np.load(weights)

	for name, param in model.namedparams():
		if param is model.fc.b:
			return content[f"{prefix}{name}"].shape[0]



def load_classifier(args):

	weights = Path(args.classifier)
	label_mapping = parser.load_yaml(weights.parent / "unq2orig_labels.yml")

	opts = parser.load_yaml(weights.parent / "meta/args.yml")
	logging.info(f"Loading classifier from {weights}")

	params = clf_module.get_params(opts)
	clf_cls = params["classifier_cls"]
	clf_kwargs = params["classifier_kwargs"]
	model_kwargs = params["model_kwargs"]

	input_size = Size(opts.input_size)
	model = ModelFactory.new(opts.model_type, input_size=input_size, **model_kwargs)
	clf = clf_cls(model=model, **clf_kwargs)

	n_classes = infer_from_weights(weights, model)
	model.reinitialize_clf(n_classes)
	clf.load(weights, n_classes=n_classes, finetune=False, strict=True)


	return clf, label_mapping


class Dataset(chainer.dataset.DatasetMixin):

	def __init__(self, root, *, extensions=[".jpg", ".png", ".jpeg"]):
		images = []
		self.root = Path(root)
		for path, folders, files in os.walk(self.root):
			path = Path(path)
			for fname in files:
				fpath = path / fname

				if fpath.suffix.lower() not in extensions:
					continue

				images.append(fpath)

		logging.info(f"Found {len(images):,d} images under {self.root}")
		self.images = sorted(images)

	def __len__(self):
		return len(self.images)

	def get_example(self, i):
		return data_utils.read_image(self.images[i], n_retries=3)


def project_back_bbox(bboxes, orig, X):
	_orig = orig.transpose(2, 0, 1)
	C, H, W = _orig.shape
	c, h, w = X.shape

	size = min(H, W)
	_, params = tr.center_crop(_orig, (size, size), return_param=True)

	x_offset = params["x_slice"].start
	y_offset = params["y_slice"].start

	bboxes = tr.resize_bbox(bboxes, (h,w), (size, size))

	bboxes[:, 0] += y_offset
	bboxes[:, 1] += x_offset
	bboxes[:, 2] += y_offset
	bboxes[:, 3] += x_offset

	return bboxes

def detect(orig, detector, *, is_blob_det: bool):
	X = orig.transpose(2,0,1).astype(np.float32)
	size = tuple(detector.model.input_size)

	if not is_blob_det:
		X = tr.resize(X, size)

	X -= BBoxDataset.mean
	_bboxes, _, _ = detector.predict(X[None], preset="visualize")

	bboxes = _bboxes[0]
	if len(bboxes) != 0:
		return tr.resize_bbox(bboxes, X.shape[1:], orig.shape[:-1])
	else:
		return bboxes

def classify(orig, bboxes, classifier):
	predictions = []
	model = classifier.model
	for y0, x0, y1, x1 in bboxes:
		w, h = x1 - x0, y1 - y0
		size = int(max([w, h]))

		dw, dh = (size - w) / 2, (size - h) / 2
		y0, y1 = max(int(y0 - dh), 0), int(y0 - dh + size)
		x0, x1 = max(int(x0 - dw), 0), int(x0 - dw + size)
		crop = orig[y0:y1, x0:x1]
		X = model.prepare(crop, keep_ratio=False)[None]
		pred = model(model.xp.array(X))

		if isinstance(pred, tuple):
			pred = pred[0]

		pred.to_cpu()
		pred = chainer.as_array(pred)

		predictions.extend(pred.argmax(axis=1))

	return predictions

def show(orig, fname, bboxes, predictions, label_mapping):
	fig, ax = plt.subplots()

	ax.imshow(orig)
	ax.set_title(fname)

	for bbox, pred in zip(bboxes, predictions):
		y0, x0, y1, x1 = bbox
		w, h = x1 - x0, y1 - y0

		ax.add_patch(plt.Rectangle((x0, y0), w, h, fill=False))

		ax.text(x0, y0, label_mapping.get(pred, "NOT FOUND"),
			va="bottom",
			bbox=dict(facecolor='grey', alpha=0.5))

	plt.show()
	plt.close()


def main(args):
	if args.mode == "extract":
		assert not Path(args.output).exists(), \
			f"Destination already exists: {args.output}!"
	data = Dataset(args.data)
	GPU = args.gpu[0]
	device = chainer.get_device(GPU)
	if GPU >= 0:
		GiB = 1024**3
		chainer.backends.cuda.set_max_workspace_size(1 * GiB)

	logging.info(f"Using {device!r:}")

	device.use()

	detector, is_blob_det = load_detector(args)
	classifier, label_mapping = load_classifier(args)

	detector.to_device(device)
	classifier.to_device(device)

	results = []


	for i, im in enumerate(tqdm(data)):
		fname = data.images[i].relative_to(args.data)
		orig = data_utils.asarray(im)

		bboxes = detect(orig, detector, is_blob_det=is_blob_det)
		predictions = classify(orig, bboxes, classifier)

		if args.mode == "visualize":
			show(orig, fname, bboxes, predictions, label_mapping)

		results.append(
			dict(
				image=str(fname),
				objects=[
					dict(
						x0=int(box[1]), y0=int(box[0]),
						x1=int(box[3]), y1=int(box[2]),
						prediction=int(pred)
					) for box, pred in zip(bboxes, predictions)
				]
		))


	if args.mode == "extract":
		output = dict(
			root=args.data,
			classifier=args.classifier,
			detector=args.detector,
			results=results,
			label_mapping=dict(label_mapping)
		)
		parser.dump_yaml(args.output, output)


chainer.config.cv_resize_backend = "cv2"
with chainer.using_config("train", False), chainer.no_backprop_mode():
	main(parser.parse_args())
