""" Test  """
import sys
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

import pytest
from _pytest.capture import CaptureFixture

from paneldata_pipeline.check_relations import parse_arguments


class TestCheckRelations(TestCase):
    """Test cli and functions of check_relations module."""

    capsys: CaptureFixture

    def test_parse_arguments(self) -> None:
        """Define the expected arguments of the shell entrypoint."""

        arguments = [
            "check_relations.py",
            "-i",
            "./input/folder",
            "-r",
            "./relations.json",
        ]

        with patch.object(sys, "argv", arguments):
            _parsed_arguments = vars(parse_arguments())

        argument_keys = ["input_folder", "relational_file"]

        for key in argument_keys:
            self.assertIn(key, _parsed_arguments.keys())

        self.assertEqual(Path(arguments[2]).resolve(), _parsed_arguments["input_folder"])
        self.assertEqual(
            Path(arguments[4]).resolve(), _parsed_arguments["relational_file"]
        )
        for boolean_field in argument_keys[-4:]:
            self.assertTrue(_parsed_arguments[boolean_field])

    @pytest.mark.usefixtures("capsys_unittest")  # type: ignore[misc]
    def test_help_message(self) -> None:
        """Help message should be printed with the -h flag and missing argument input."""
        arguments = ["check_relations.py", "-h"]

        with patch.object(sys, "argv", arguments[:1]):
            with self.assertRaises(SystemExit):
                parse_arguments()
        no_flag_output = self.capsys.readouterr().out  # type: ignore[no-untyped-call]

        with patch.object(sys, "argv", arguments):
            with self.assertRaises(SystemExit):
                parse_arguments()
        h_flag_output = self.capsys.readouterr().out  # type: ignore[no-untyped-call]

        self.assertEqual(h_flag_output, no_flag_output)
