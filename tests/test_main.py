""" Test functionality related to the packages entrypoint. """
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from paneldata_pipeline.__main__ import main, parse_arguments


class TestMainModule(unittest.TestCase):  # pylint: disable=missing-docstring
    def test_main_method(self):
        """ Test entrypoint of the package. """
        self.assertIsInstance(main, object)

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
