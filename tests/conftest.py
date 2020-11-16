"""Provide general pytest fixtures."""
import glob
from pathlib import Path
from shutil import copy, rmtree
from tempfile import mkdtemp
from typing import Dict, Generator

import pytest
from _pytest.capture import CaptureFixture
from _pytest.fixtures import FixtureRequest
from _pytest.logging import LogCaptureFixture


@pytest.fixture(name="capsys_unittest")  # type: ignore[misc]
def _capsys_unittest(
    capsys: Generator[CaptureFixture, None, None], request: FixtureRequest
) -> None:
    request.instance.capsys = capsys


@pytest.fixture(name="caplog_unittest")  # type: ignore[misc]
def _caplog_unittest(caplog: LogCaptureFixture, request: FixtureRequest) -> None:
    request.instance.caplog = caplog


@pytest.fixture(name="temp_directories")  # type: ignore[misc]
def _temp_directories(request: FixtureRequest) -> Generator[Dict[str, Path], None, None]:
    """Provide temporary input and output folders."""
    temp_directories = dict()
    temp_directories["input_path"] = Path(mkdtemp()).absolute()
    temp_directories["output_path"] = Path(mkdtemp()).absolute()

    data_path = Path("./tests/test_data/").absolute()
    for _file in glob.glob(f"{data_path}/*.csv"):
        copy(_file, temp_directories["input_path"])
    for _file in glob.glob(f"{data_path}/*.json"):
        copy(_file, temp_directories["input_path"])

    if request.instance:
        request.instance.temp_directories = temp_directories
        request.instance.concepts_path = temp_directories["input_path"].joinpath(
            "concepts.csv"
        )
        request.instance.variables_path = temp_directories["input_path"].joinpath(
            "variables.csv"
        )
        request.instance.questions_path = temp_directories["input_path"].joinpath(
            "questions.csv"
        )
    yield temp_directories
    for directory in temp_directories.values():
        rmtree(directory)
