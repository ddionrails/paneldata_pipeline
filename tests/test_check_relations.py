""" Test  """
import json
import sys
from pathlib import Path
from typing import Dict
from unittest import TestCase
from unittest.mock import patch

import pytest
from _pytest.capture import CaptureFixture

from paneldata_pipeline.check_relations import (
    FileRelationInformation,
    parse_arguments,
    read_relations,
    relations_exist,
)


@pytest.mark.usefixtures("temp_directories")
class TestCheckRelations(TestCase):
    """Test non cli related parts of check_relations module."""

    temp_directories: Dict[str, Path]

    def test_relation_file_reading(self) -> None:
        """File describing relations should be read correctly."""
        base_path: Path = self.temp_directories["input_path"]
        relational_file = base_path.joinpath("relations.json")
        with open(relational_file, "w+") as file:
            json.dump(RELATIONAL_FILE_CONTENT, file)
        relations = read_relations(folder_path=base_path)
        self.assertIsInstance(relations, list)
        for index, relation in enumerate(relations):
            self.assertEqual(RELATIONAL_FILE_CONTENT[index], relation)

    def test_correct_relations(self) -> None:
        """The relational check should pass here."""
        base_path: Path = self.temp_directories["input_path"]
        to_relation = FileRelationInformation(
            file=base_path.joinpath("instruments.csv"), fields=["study", "name"]
        )
        from_relation = FileRelationInformation(
            file=base_path.joinpath("questions.csv"), fields=["study", "instrument"]
        )
        result = relations_exist(target=to_relation, origins=[from_relation])
        self.assertTrue(result)

    def test_incorrect_relations(self) -> None:
        """The relational check should pass here."""
        base_path: Path = self.temp_directories["input_path"]
        incorrect_row = "test-study,none-existent,a,,,,,,,,,,,,"
        to_relation = FileRelationInformation(
            file=base_path.joinpath("instruments.csv"), fields=["study", "name"]
        )
        from_relation = FileRelationInformation(
            file=base_path.joinpath("questions.csv"), fields=["study", "instrument"]
        )
        with open(base_path.joinpath("questions.csv"), "a") as questions_file:
            questions_file.write(incorrect_row)
        result = relations_exist(target=to_relation, origins=[from_relation])
        self.assertFalse(result)


class TestCLI(TestCase):
    """Test cli related parts in check_relations module."""

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


RELATIONAL_FILE_CONTENT = [
    {
        "file": "analysis_units.csv",
        "fields": ["name"],
        "relations_from": [
            {"file": "datasets.csv", "fields": ["analysis_unit"]},
            {"file": "instruments.csv", "fields": ["analysis_unit"]},
        ],
    },
    {
        "file": "answers.csv",
        "fields": ["study", "instrument", "answer_list"],
        "relations_from": [
            {"file": "questions.csv", "fields": ["study", "instrument", "answer_list"]}
        ],
    },
]
