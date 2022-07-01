""" Entrypoint and functions for cli to test relations between metadata files."""
import argparse
import json
import logging
import sys
from copy import deepcopy
from datetime import datetime
from importlib import resources
from os import remove
from pathlib import Path
from typing import Any, Generator, List, TypedDict

from frictionless import validate
from frictionless.error import Error as FrictionlessError
from frictionless.errors.label import IncorrectLabelError, MissingLabelError
from tabulate import tabulate

IncorrectLabelError.template = (
    'Column at position "{fieldPosition}" should be "{fieldName}" but is "{label}".'
)
MissingLabelError.template = (
    'Column at position "{fieldPosition}" is missing. Should be "{fieldName}".'
)


LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

HANDLER = logging.StreamHandler(sys.stdout)
HANDLER.setLevel(logging.DEBUG)
FORMATTER = logging.Formatter("%(levelname)s - %(message)s")
HANDLER.setFormatter(FORMATTER)
LOGGER.addHandler(HANDLER)


class DataPackage(TypedDict):
    """Describe root structure of a datapackage."""

    profile: str
    resources: List[Any]


data_package_base: DataPackage = {"profile": "tabular-data-package", "resources": []}


def main() -> None:
    """Entrypoint for the CLI."""
    arguments = parse_arguments()
    if arguments.debug:
        LOGGER.setLevel(logging.DEBUG)

    metadata_location = arguments.input_folder

    data_package = deepcopy(data_package_base)
    timestamp = datetime.now().strftime("%d%m%Y%H%M%S%f")

    metadata_file_names = {path.stem for path in metadata_location.glob("*.csv")}
    for resource in _get_path_to_resources():
        if resource.stem in metadata_file_names:
            with open(resource, encoding="utf8") as _file:
                data_package["resources"].append(json.load(_file))
        else:
            print(f"Metadata file {resource.name} is not present.")

    data_package_location = metadata_location / f"{timestamp}datapackage.json"

    with open(data_package_location, "w", encoding="utf8") as package:
        json.dump(data_package, package)

    report = validate(data_package_location, skip_errors=["extra-cell", "extra-label"])
    errors = False
    for task in report.tasks:
        if task.errors:
            if errors:
                print("\n" * 2)
            print(
                tabulate(
                    [[f"Checking: {metadata_location / task.resource['path']}"]],
                    tablefmt="grid",
                )
            )
            print(task.to_summary())
            _print_error_table(task.errors)
            errors = True

    remove(data_package_location)
    if errors:
        sys.exit(1)
    sys.exit(0)


def _print_error_table(errors: List[FrictionlessError]) -> None:
    missing_labels = False
    error_message_rows = []
    for error in errors:
        if error.code == "missing-label":
            missing_labels = True
        if error.code == "missing-cell" and missing_labels:
            continue
        error_message_rows.append([error.code, error.message])
    print(tabulate(error_message_rows, headers=["code", "message"], tablefmt="grid"))


def _get_path_to_resources() -> Generator[Path, None, None]:

    with resources.path("paneldata_pipeline", "resources") as resource_folder:
        for resource in resource_folder.glob("*.json"):
            yield resource


def parse_arguments() -> argparse.Namespace:
    """Set up arguments and parse them."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--input-folder", help="Path to the metadata csv files.", type=_full_path
    )
    parser.add_argument(
        "-d", "--debug", help="Activate debug output", action="store_true", default=False
    )
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    return parser.parse_args()


def _full_path(path: str) -> Path:
    return Path(path).resolve()


if __name__ == "__main__":
    main()
