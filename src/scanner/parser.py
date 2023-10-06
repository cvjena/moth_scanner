from cvargparse import Arg
from cvargparse import BaseParser
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
    main_parser = BaseParser()

    _common_parser = GPUParser([
        Arg("data"),
    ], add_help=False, nologging=True)

    add_model_args(_common_parser)

    subp = main_parser.add_subparsers(
        title="Execution modes",
        dest="mode",
        required=True
    )

    parser = subp.add_parser("visualize",
        help="Shows the outputs of the scanner",
        parents=[_common_parser])

    parser = subp.add_parser("extract",
        help="Shows the outputs of the scanner",
        parents=[_common_parser])

    parser.add_args([
        Arg("--output", "-out", required=True)
    ])


    return main_parser.parse_args(*args, **kw)


def load_yaml(path):
    with open(path) as f:
        return munchify(yaml.load(f, Loader=Loader))

def dump_yaml(path, content, **kwargs):
    with open(path, "w") as f:
        yaml.dump(content, f, Dumper=Dumper, **kwargs)



__all__ = ["parse_args"]
