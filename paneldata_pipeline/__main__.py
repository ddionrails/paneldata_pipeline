""" Entrypoint related functions of the package. """

import argparse
from pathlib import Path
from typing import Dict

from paneldata_pipeline.fill_ddionrails import main as fill_ddionrails


def main():
    """ Entrypoint of the package. """
    fill_ddionrails(**parse_arguments())


def parse_arguments() -> Dict[str, Path]:
    """Setup arguments and parse them."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input-folder", help="Path to the ", type=_full_path)
    parser.add_argument("-o", "--output-folder", type=_full_path)
    parser.add_argument("-r", "--variable-relations", action="store_true", default=False)
    parser.add_argument(
        "-u", "--unify-instrument-data", action="store_true", default=False
    )
    parser.add_argument("-q", "--question-relations", action="store_true", default=False)
    parser.add_argument(
        "-g",
        "--generate-topic-tree",
        dest="topic_tree",
        action="store_true",
        default=False,
    )
    _parsed_arguments = parser.parse_args()

    return vars(_parsed_arguments)


def _full_path(path: str) -> Path:
    return Path(path).resolve()
