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
    parser.add_argument("-i", "--input-folder", dest="input_folder", help="Path to the ")
    parser.add_argument("-o", "--output-folder", dest="output_folder")
    _parsed_arguments = parser.parse_args()

    return {
        "input_folder": Path(_parsed_arguments.input_folder).resolve(),
        "output_folder": Path(_parsed_arguments.output_folder).resolve(),
    }
