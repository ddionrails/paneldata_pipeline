""" Test functionality related to the packages entrypoint. """
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from paneldata_pipeline.__main__ import main, parse_arguments


class TestMainModule(unittest.TestCase):  # pylint: disable=missing-docstring
    def test_parse_arguments(self):
        """Define the expected arguments of the shell entrypoint."""

        arguments = [
            "__main__.py",
            "-i",
            "./input/folder",
            "-o",
            "./output/folder",
            "-r",
            "-u",
            "-q",
            "-g",
        ]

        with patch.object(sys, "argv", arguments):
            _parsed_arguments = parse_arguments()

        argument_keys = [
            "input_folder",
            "output_folder",
            "variable_relations",
            "unify_instrument_data",
            "question_relations",
            "topic_tree",
        ]

        for key in argument_keys:
            self.assertIn(key, _parsed_arguments.keys())

        self.assertEqual(Path(arguments[2]).resolve(), _parsed_arguments["input_folder"])
        self.assertEqual(Path(arguments[4]).resolve(), _parsed_arguments["output_folder"])
        for boolean_field in argument_keys[2:]:
            self.assertTrue(_parsed_arguments[boolean_field])


class TestMainModuleInteraction(unittest.TestCase):
    """Tests concerning the program flow during cli calls."""

    @staticmethod
    @patch("paneldata_pipeline.__main__.merge_instruments")
    @patch("paneldata_pipeline.__main__.questions_from_generations")
    @patch("paneldata_pipeline.__main__.preprocess_transformations")
    @patch("paneldata_pipeline.__main__.TopicParser")
    def test_function_dispatcher(
        merge_instruments: MagicMock,
        questions_from_generations: MagicMock,
        preprocess_transformations: MagicMock,
        topic_parser: MagicMock,
    ):
        """Define the expected arguments of the shell entrypoint."""

        arguments = [
            "__main__.py",
            "-i",
            "./input/folder",
            "-o",
            "./output/folder",
            "-r",
            "-u",
            "-q",
            "-g",
        ]

        with patch.object(sys, "argv", arguments[:5]):
            _parsed_arguments = main()

        merge_instruments.assert_not_called()
        questions_from_generations.assert_not_called()
        preprocess_transformations.assert_not_called()
        topic_parser.assert_not_called()

        with patch.object(sys, "argv", arguments):
            main()

        merge_instruments.assert_called_once()
        questions_from_generations.assert_called_once()
        preprocess_transformations.assert_called_once()
        topic_parser.assert_called_once()
