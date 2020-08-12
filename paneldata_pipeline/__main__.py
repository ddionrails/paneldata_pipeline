""" Entrypoint related functions of the package. """

import argparse
from pathlib import Path
from typing import TypedDict

from paneldata_pipeline.merge_instruments import merge_instruments
from paneldata_pipeline.questions_variables import questions_from_generations
from paneldata_pipeline.topics import TopicParser
from paneldata_pipeline.transformations import preprocess_transformations


def main() -> None:
    """ Entrypoint of the package. """
    _parsed_arguments = parse_arguments()
    input_folder = _parsed_arguments["input_folder"]
    output_folder = _parsed_arguments["output_folder"]
    if _parsed_arguments["unify_instrument_data"]:
        merge_instruments(input_folder, output_folder)
    if _parsed_arguments["question_relations"]:
        # TODO: Fix arguments here
        questions_from_generations()
    if _parsed_arguments["variable_relations"]:
        # TODO: Fix arguments here
        preprocess_transformations()
    if _parsed_arguments["topic_tree"]:
        # TODO: Fix arguments here
        TopicParser()


class CLIArgs(TypedDict, total=False):
    """Define cli argument types."""

    input_folder: Path
    output_folder: Path
    variable_relations: bool
    unify_instrument_data: bool
    question_relations: bool
    topic_tree: bool


def parse_arguments() -> CLIArgs:
    """Setup arguments and parse them."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input-folder", help="Path to the ", type=_full_path)
    parser.add_argument("-o", "--output-folder", type=_full_path)
    parser.add_argument("-r", "--variable-relations", action="store_true", default=False)
    parser.add_argument(
        "-u", "--unify-instrument-data", action="store_true", default=False
    )
    parser.add_argument("-q", "--question-relations", action="store_true", default=False)
    parser.add_argument("-g", "--generate-topic-tree", action="store_true", default=False)
    _parsed_arguments = parser.parse_args()

    return {
        "input_folder": _parsed_arguments.input_folder,
        "output_folder": _parsed_arguments.output_folder,
        "variable_relations": _parsed_arguments.variable_relations,
        "unify_instrument_data": _parsed_arguments.unify_instrument_data,
        "question_relations": _parsed_arguments.question_relations,
        "topic_tree": _parsed_arguments.generate_topic_tree,
    }


def _full_path(path: str) -> Path:
    return Path(path).resolve()
