""" Test functionality related to the packages entrypoint. """
import sys
import unittest
from pathlib import Path
from typing import Dict, Generator
from unittest.mock import MagicMock, patch

import pytest
from _pytest.capture import CaptureFixture
from _pytest.fixtures import FixtureRequest

from paneldata_pipeline.__main__ import main, parse_arguments


@pytest.fixture(name="capsys_unittest")  # type: ignore[misc]
def _capsys_unittest(
    capsys: Generator[CaptureFixture, None, None], request: FixtureRequest
) -> None:
    request.instance.capsys = capsys


class TestMainModule(unittest.TestCase):  # pylint: disable=missing-docstring

    capsys: CaptureFixture

    def test_parse_arguments(self) -> None:
        """Define the expected arguments of the shell entrypoint."""

        arguments = [
            "__main__.py",
            "-i",
            "./input/folder",
            "-o",
            "./output/folder",
            "--study",
            "some-study",
            "--version",
            "v1",
            "-r",
            "-u",
            "-q",
            "-g",
        ]

        with patch.object(sys, "argv", arguments):
            _parsed_arguments = vars(parse_arguments())

        argument_keys = [
            "input_folder",
            "output_folder",
            "study",
            "version",
            "variable_relations",
            "unify_instrument_data",
            "question_relations",
            "generate_topic_tree",
        ]

        for key in argument_keys:
            self.assertIn(key, _parsed_arguments.keys())

        self.assertEqual(Path(arguments[2]).resolve(), _parsed_arguments["input_folder"])
        self.assertEqual(Path(arguments[4]).resolve(), _parsed_arguments["output_folder"])
        for boolean_field in argument_keys[-4:]:
            self.assertTrue(_parsed_arguments[boolean_field])

    @pytest.mark.usefixtures("capsys_unittest")  # type: ignore[misc]
    def test_help_message(self) -> None:
        """Help message should be printed with the -h flag and missing argument input."""
        arguments = ["__main__.py", "-h"]

        with patch.object(sys, "argv", arguments):
            with self.assertRaises(SystemExit):
                parse_arguments()
        h_flag_output = self.capsys.readouterr().out  # type: ignore[no-untyped-call]

        with patch.object(sys, "argv", arguments[:1]):
            with self.assertRaises(SystemExit):
                parse_arguments()
        no_flag_output = self.capsys.readouterr().out  # type: ignore[no-untyped-call]

        self.assertEqual(h_flag_output, no_flag_output)


class TestMainModuleInteraction(unittest.TestCase):
    """Tests concerning the program flow during cli calls."""

    temp_directories: Dict[str, Path]

    @staticmethod
    @patch("paneldata_pipeline.__main__.preprocess_transformations")
    @patch("paneldata_pipeline.__main__.TopicParser")
    @patch("paneldata_pipeline.__main__.questions_from_generations")
    @patch("paneldata_pipeline.__main__.merge_instruments")
    def test_function_dispatcher(
        merge_instruments: MagicMock,
        questions_from_generations: MagicMock,
        topic_parser: MagicMock,
        preprocess_transformations: MagicMock,
    ) -> None:
        """Define the expected arguments of the shell entrypoint."""

        arguments = [
            "__main__.py",
            "-i",
            "./input/folder",
            "-o",
            "./output/folder",
            "--study",
            "some-study",
            "--version",
            "v1",
            "-r",
            "-u",
            "-q",
            "-g",
        ]

        with patch.object(sys, "argv", arguments[:9]):
            main()

        merge_instruments.assert_not_called()
        questions_from_generations.assert_not_called()
        preprocess_transformations.assert_not_called()
        topic_parser.assert_not_called()

        with patch.object(sys, "argv", arguments):
            main()

        path_arguments = {
            "input_folder": Path(arguments[2]).resolve(),
            "output_folder": Path(arguments[4]).resolve(),
        }

        merge_instruments.assert_called_once_with(**path_arguments)
        questions_from_generations.assert_called_once_with(
            **{"version": arguments[8]}, **path_arguments
        )
        topic_parser.assert_called_once_with(**path_arguments)
        preprocess_transformations.assert_called_once_with(
            **{"study": arguments[6], "version": arguments[8]}, **path_arguments
        )

    @pytest.mark.usefixtures("temp_directories")
    def test_full_run(self):
        """Test a full run with all flags set."""
        arguments = [
            "__main__.py",
            "-i",
            f'{self.temp_directories["input_path"]}',
            "-o",
            f'{self.temp_directories["output_path"]}',
            "--study",
            "some-study",
            "--version",
            "v1",
            "-r",
            "-u",
            "-q",
            "-g",
        ]

        with patch.object(sys, "argv", arguments):
            main()
        breakpoint()
