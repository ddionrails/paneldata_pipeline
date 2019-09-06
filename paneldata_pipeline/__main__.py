# -*- coding: utf-8 -*-
""" Entrypoint related functions of the package. """

import json
from pathlib import Path
from typing import Tuple

import click

from .questions import preprocess_questions
from .topics import TopicParser


def setup_paths(input_path: str, output_path: str) -> Tuple[Path, Path]:
    """Returns pathlib.Path objects (and creates output_path if necessary)."""
    output_path = Path(output_path)
    # Create output path, if it does not exist yet
    output_path.mkdir(exist_ok=True)
    return Path(input_path), output_path


@click.group()
def main() -> None:
    """paneldata-pipeline CLI"""


@main.command()
@click.argument("input_path", type=click.Path(exists=True))
@click.argument("output_path", type=click.Path())
def questions(input_path: str, output_path: str) -> None:
    """Preprocess questions and answers."""
    input_path, output_path = setup_paths(input_path, output_path)
    for (instrument_name, instrument_list) in preprocess_questions(input_path):
        filename = output_path.joinpath(instrument_name).with_suffix(".json")
        with open(str(filename), "w") as outfile:
            json.dump(instrument_list, outfile, indent=2)


@main.command()
@click.argument("input_path", type=click.Path(exists=True))
@click.argument("output_path", type=click.Path())
def topics(input_path: str, output_path: str) -> None:
    """Run TopicParser to create JSON topiclist."""
    input_path, output_path = setup_paths(input_path, output_path)
    TopicParser(
        input_path.joinpath("topics.csv"), input_path.joinpath("concepts.csv")
    ).to_json(output_path.joinpath("topics.json"))
