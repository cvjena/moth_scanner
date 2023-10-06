from cvargparse import Arg
from cvargparse import GPUParser

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

import yaml

from munch import munchify


def add_model_args(parser: GPUParser):

    _clf_args = [
        Arg("--classifier", "-clf",
            required=True,
            help="path to the classifier weights"),
    ]

    _det_args = [
        Arg("--detector", "-det",
            required=True,
            help="path to the detection weights"),

    ]


    parser.add_args(_clf_args, group_name="Classifier arguments")
    parser.add_args(_det_args, group_name="Detector arguments")

def parse_args(*args, **kw):

    parser = GPUParser([
        Arg("data"),
        Arg.int("--n_jobs", "-j", default=1),

    ])

    # add_dataset_args(parser)
    add_model_args(parser)


    return parser.parse_args(*args, **kw)


def load_yaml(path):
    with open(path) as f:
        return munchify(yaml.load(f, Loader=Loader))

def dump_yaml(path, content, **kwargs):
    with open(path, "w") as f:
        yaml.dump(content, f, Dumper=Dumper, **kwargs)



__all__ = ["parse_args"]
