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

        arguments = ["__main__.py", "-i", "./input/folder", "-o", "./output/folder"]

        with patch.object(sys, "argv", arguments):
            _parsed_arguments = parse_arguments()

        self.assertIn("input_folder", _parsed_arguments.keys())
        self.assertIn("output_folder", _parsed_arguments.keys())
        self.assertEqual(Path(arguments[2]).resolve(), _parsed_arguments["input_folder"])
        self.assertEqual(Path(arguments[4]).resolve(), _parsed_arguments["output_folder"])
