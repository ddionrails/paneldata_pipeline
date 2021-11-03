""" Entrypoint and functions for cli to test relations between metadata files."""
import argparse
import logging
import sys
from csv import DictReader
from json import decoder, load
from pathlib import Path
from typing import List, TypedDict

LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

HANDLER = logging.StreamHandler(sys.stdout)
HANDLER.setLevel(logging.DEBUG)
FORMATTER = logging.Formatter("%(levelname)s - %(message)s")
HANDLER.setFormatter(FORMATTER)
LOGGER.addHandler(HANDLER)


class RelationOrigin(TypedDict):
    """Information about a file a relation is originating from."""

    file: Path
    fields: List[str]


class RelationTarget(TypedDict):
    """Information of a file relations are pointing towards."""

    file: Path
    fields: List[str]
    relations_from: List[RelationOrigin]


def main() -> None:
    """Entrypoint for the CLI."""
    arguments = parse_arguments()
    if arguments.debug:
        LOGGER.setLevel(logging.DEBUG)
    try:
        relations = read_relations(arguments.relational_file)
    except FileNotFoundError:
        LOGGER.error("No relational file exists at %s", arguments.relational_file)
        sys.exit(1)
    except decoder.JSONDecodeError as error:
        LOGGER.error("Error in JSON format of %s: %s", arguments.relational_file, error)
        sys.exit(1)

    all_relations_exist = set()
    all_relations_exist.add(check_cat_question_items(arguments.input_folder))

    for relation in relations:
        relation["file"] = arguments.input_folder.joinpath(relation["file"])
        relation["relations_from"] = [
            RelationOrigin(
                file=arguments.input_folder.joinpath(origin["file"]),
                fields=origin["fields"],
            )
            for origin in relation["relations_from"]
        ]
        try:
            all_relations_exist.add(relations_exist(relation, relation["relations_from"]))
        except FileNotFoundError as error:
            LOGGER.debug(
                "A file from the config is not present in the input directory: %s", error
            )

    if False in all_relations_exist:
        sys.exit(1)
    sys.exit(0)


def check_cat_question_items(input_folder: Path) -> bool:
    """Check if all questions with scale cat have a value for answer_list."""
    LOGGER.info("Checking if all cat questions have answer_list values.")
    questions_path = input_folder.joinpath("questions.csv")
    passed = True
    if not questions_path.exists():
        return True
    with open(input_folder.joinpath("questions.csv"), "r", encoding="utf8") as file:
        reader = DictReader(file)
        for row in reader:
            if row["scale"] != "cat":
                continue
            if row["answer_list"] == "":
                passed = False
                LOGGER.info(
                    "Question %s has no answer_list.",
                    {key: row[key] for key in ["study", "instrument", "name", "item"]},
                )
    return passed


def read_relations(file_path: Path) -> List[RelationTarget]:
    """Read config file containing relational information."""
    with open(file_path) as file:
        relations: List[RelationTarget] = load(file)
    return relations


def parse_arguments() -> argparse.Namespace:
    """Set up arguments and parse them."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--input-folder", help="Path to the input metadata files.", type=_full_path
    )
    parser.add_argument(
        "-r",
        "--relational-file",
        help="JSON file containing relational information between files",
        type=_full_path,
    )
    parser.add_argument(
        "-d", "--debug", help="Activate debug output", action="store_true", default=False
    )
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    return parser.parse_args()


def relations_exist(target: RelationOrigin, origins: List[RelationOrigin]) -> bool:
    """Check if reference from origin file to a target file exists."""
    with open(target["file"], "r") as _file:
        _reader = DictReader(_file)
        keypairs = set()
        for row in _reader:
            _keypair = list()
            for field in target["fields"]:
                _keypair.append(row[field])
            keypairs.add(tuple(_keypair))

    all_relations_exist = True
    for origin in origins:
        with open(origin["file"], "r") as _file:
            _reader = DictReader(_file)
            LOGGER.info(
                ("Checking relation to " "%s:%s from " "%s:%s"),
                target["file"].name,
                target["fields"],
                origin["file"].name,
                origin["fields"],
            )
            for row_number, row in enumerate(_reader, start=2):
                _keypair = list()
                for field in origin["fields"]:
                    _keypair.append(row.get(field, ""))
                # Skip check if no relation is defined inside the fields.
                if "" in _keypair:
                    continue
                if tuple(_keypair) not in keypairs:
                    LOGGER.info("Relation target in line %d does not exist.", row_number)
                    all_relations_exist = False

    return all_relations_exist


def _full_path(path: str) -> Path:
    return Path(path).resolve()


if __name__ == "__main__":
    main()
