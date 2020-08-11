""" Entrypoint related functions of the package. """

import argparse
from pathlib import Path


def main():
    """ Entrypoint of the package. """
    pass  # pylint: disable=unnecessary-pass


def parse_arguments():
    """Setup arguments and parse them."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input-folder", dest="input_folder", help="Path to the ")
    parser.add_argument("-o", "--output-folder", dest="output_folder")
    _parsed_arguments = parser.parse_args()

    return {
        "input_folder": Path(_parsed_arguments.input_folder).resolve(),
        "output_folder": Path(_parsed_arguments.output_folder).resolve(),
    }
