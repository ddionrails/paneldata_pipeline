""" Entrypoint related functions of the package. """

import argparse
import sys
from pathlib import Path

from paneldata_pipeline.concepts import extract_implicit_concepts
from paneldata_pipeline.merge_instruments import merge_instruments
from paneldata_pipeline.questions_variables import questions_from_generations
from paneldata_pipeline.topics import TopicParser
from paneldata_pipeline.transformations import preprocess_transformations


def main() -> None:
    """ Entrypoint of the package. """
    _parsed_arguments = parse_arguments()
    input_folder: Path = _parsed_arguments.input_folder
    output_folder: Path = _parsed_arguments.output_folder
    if input_folder.joinpath("concepts.csv").exists():
        extract_implicit_concepts(
            input_folder,
            input_folder.joinpath("concepts.csv"),
            output_folder.joinpath("concepts.csv"),
        )
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
    parser.add_argument(
        "-i", "--input-folder", help="Path to the input metadata files.", type=_full_path
    )
    parser.add_argument(
        "-o",
        "--output-folder",
        help="Target directory for created files.",
        type=_full_path,
    )
    parser.add_argument(
        "-s", "--study", help="Name of the study, that is processed.", type=str
    )
    parser.add_argument(
        "-w", "--version", help="Name of the wave/version of the data.", type=str
    )
    parser.add_argument(
        "-r",
        "--variable-relations",
        help=(
            "Clean up relational file for variables."
            "Creates a new file with all transitive relations "
            "and with intermediate variables removed."
        ),
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-u",
        "--unify-instrument-data",
        help=(
            "Gather instrument metadata from several csv files in central JSON files. "
            "Creates one JSON file per instrument."
        ),
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-q",
        "--question-relations",
        help="Same as -r but for question relations.",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-g",
        "--generate-topic-tree",
        help=(
            "Generate hierarchical topic tree as JSON file. "
            "Reads from topics.csv and concepts.csv."
        ),
        action="store_true",
        default=False,
    )
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    return parser.parse_args()


def _full_path(path: str) -> Path:
    return Path(path).resolve()


if __name__ == "__main__":
    main()
