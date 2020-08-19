""" Entrypoint related functions of the package. """

import argparse
from pathlib import Path

from paneldata_pipeline.merge_instruments import merge_instruments
from paneldata_pipeline.questions_variables import questions_from_generations
from paneldata_pipeline.topics import TopicParser
from paneldata_pipeline.transformations import preprocess_transformations


def main() -> None:
    """ Entrypoint of the package. """
    _parsed_arguments = parse_arguments()
    input_folder = _parsed_arguments.input_folder
    output_folder = _parsed_arguments.output_folder
    if _parsed_arguments.unify_instrument_data:
        merge_instruments(input_folder=input_folder, output_folder=output_folder)
    if _parsed_arguments.question_relations:
        questions_from_generations(
            version=_parsed_arguments.version,
            input_folder=input_folder,
            output_folder=output_folder,
        )
    if _parsed_arguments.variable_relations:
        preprocess_transformations(
            study=_parsed_arguments.study,
            version=_parsed_arguments.version,
            input_folder=input_folder,
            output_folder=output_folder,
        )
    if _parsed_arguments.generate_topic_tree:
        TopicParser(input_folder=input_folder, output_folder=output_folder).to_json()


def parse_arguments() -> argparse.Namespace:
    """Set up arguments and parse them."""
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input-folder", help="Path to the ", type=_full_path)
    parser.add_argument("-o", "--output-folder", type=_full_path)
    parser.add_argument("-s", "--study", type=str)
    parser.add_argument("-w", "--version", type=str)
    parser.add_argument("-r", "--variable-relations", action="store_true", default=False)
    parser.add_argument(
        "-u", "--unify-instrument-data", action="store_true", default=False
    )
    parser.add_argument("-q", "--question-relations", action="store_true", default=False)
    parser.add_argument("-g", "--generate-topic-tree", action="store_true", default=False)
    return parser.parse_args()


def _full_path(path: str) -> Path:
    return Path(path).resolve()
