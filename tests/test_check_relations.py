""" Test  """

import json
import sys
from csv import DictReader
from pathlib import Path
from typing import Dict
from unittest import TestCase
from unittest.mock import patch

import pytest
from _pytest.capture import CaptureFixture
from _pytest.logging import LogCaptureFixture

from paneldata_pipeline.check_relations import (
    RelationOrigin,
    check_cat_question_items,
    main,
    parse_arguments,
    read_relations,
    relations_exist,
)
from paneldata_pipeline.concepts import extract_implicit_concepts


@pytest.mark.usefixtures("temp_directories")
class TestCheckRelations(TestCase):
    """Test non cli related parts of check_relations module."""

    caplog: LogCaptureFixture
    temp_directories: Dict[str, Path]

    def test_relation_file_reading(self) -> None:
        """File describing relations should be read correctly."""
        base_path: Path = self.temp_directories["input_path"]
        relational_file = base_path.joinpath("relations.json")
        with open(relational_file, "w+", encoding="utf8") as file:
            json.dump(RELATIONAL_FILE_CONTENT, file)
        relations = read_relations(file_path=relational_file)
        self.assertIsInstance(relations, list)
        for index, relation in enumerate(relations):
            self.assertEqual(RELATIONAL_FILE_CONTENT[index], relation)

    @pytest.mark.usefixtures("caplog_unittest")  # type: ignore[misc]
    def test_check_cat_question_items(self) -> None:
        """File describing relations should be read correctly."""
        base_path: Path = self.temp_directories["input_path"]
        questions_file = base_path.joinpath("questions.csv")
        incorrect_line = (
            "test-study,some-questionnaire,"
            "1,vsex,13786,(Geschlecht),,(Sex),,cat,,,vsex,,"
        )

        with open(questions_file, "a", encoding="utf8") as file:
            file.write(incorrect_line)
        with open(questions_file, "r", encoding="utf8") as file:
            last_line = {}
            for line in DictReader(file):
                last_line = {
                    key: line[key] for key in ["study", "instrument", "name", "item"]
                }

        self.assertFalse(check_cat_question_items(base_path))
        self.assertIn(f"Question {last_line} has no answer_list.", self.caplog.text)

    @pytest.mark.usefixtures("caplog_unittest")  # type: ignore[misc]
    def test_correct_relations(self) -> None:
        """The relational check should pass here."""
        base_path: Path = self.temp_directories["input_path"]
        to_relation = RelationOrigin(
            file=base_path.joinpath("instruments.csv"), fields=["study", "name"]
        )
        from_relation = RelationOrigin(
            file=base_path.joinpath("questions.csv"), fields=["study", "instrument"]
        )
        result = relations_exist(target=to_relation, origins=[from_relation])
        self.assertTrue(result)
        self.assertIn(
            (f"{to_relation['file'].name}:{to_relation['fields']}"),
            self.caplog.text,
        )
        self.assertIn(
            f"{from_relation['file'].name}:{from_relation['fields']}",
            self.caplog.text,
        )

    @pytest.mark.usefixtures("caplog_unittest")  # type: ignore[misc]
    def test_incorrect_relations(self) -> None:
        """The relational check should fail here."""
        base_path: Path = self.temp_directories["input_path"]
        incorrect_row = "test-study,none-existent,a,,,,,,,,,,,,"
        to_relation = RelationOrigin(
            file=base_path.joinpath("instruments.csv"), fields=["study", "name"]
        )
        from_relation = RelationOrigin(
            file=base_path.joinpath("questions.csv"), fields=["study", "instrument"]
        )
        with open(
            base_path.joinpath("questions.csv"), "a", encoding="utf8"
        ) as questions_file:
            questions_file.write(incorrect_row)
        result = relations_exist(target=to_relation, origins=[from_relation])
        self.assertIn(
            ("Relation target ['test-study', 'none-existent'] in row 4 does not exist."),
            self.caplog.text,
        )
        self.assertFalse(result)

    def test_relation_with_multiple_origins(self) -> None:
        """The relational check should pass here."""
        base_path: Path = self.temp_directories["input_path"]
        to_relation = RelationOrigin(
            file=base_path.joinpath("concepts.csv"), fields=["name"]
        )
        from_relation = [
            RelationOrigin(file=base_path.joinpath("questions.csv"), fields=["concept"])
        ]
        from_relation.append(
            RelationOrigin(file=base_path.joinpath("variables.csv"), fields=["concept"])
        )
        result = relations_exist(target=to_relation, origins=from_relation)
        self.assertFalse(result)

    def test_incorrect_relation_with_multiple_origins(self) -> None:
        """The relational check should fail here for the first file."""
        base_path: Path = self.temp_directories["input_path"]
        incorrect_row = "test-study,none-existent,a,,,,,,,,,,,,"
        to_relation = RelationOrigin(
            file=base_path.joinpath("concepts.csv"), fields=["name"]
        )
        from_relation = [
            RelationOrigin(file=base_path.joinpath("questions.csv"), fields=["concept"])
        ]
        from_relation.append(
            RelationOrigin(file=base_path.joinpath("variables.csv"), fields=["concept"])
        )
        with open(
            base_path.joinpath("questions.csv"), "a", encoding="utf8"
        ) as questions_file:
            questions_file.write(incorrect_row)
        result = relations_exist(target=to_relation, origins=from_relation)
        self.assertFalse(result)


class TestCLI(TestCase):
    """Test cli related parts in check_relations module."""

    caplog: LogCaptureFixture
    capsys: CaptureFixture
    temp_directories: Dict[str, Path]

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

    @pytest.mark.usefixtures("temp_directories")  # type: ignore[misc]
    def test_full_run(self) -> None:
        """Test a full run with all flags set."""
        base_path: Path = self.temp_directories["input_path"]

        extract_implicit_concepts(
            input_path=base_path,
            concepts_path=base_path.joinpath("concepts.csv"),
            output_concepts_path=base_path.joinpath("concepts.csv"),
        )

        arguments = [
            "check_relations.py",
            "-i",
            str(base_path),
            "-r",
            str(base_path.joinpath("relations.json")),
        ]

        with patch.object(sys, "argv", arguments):
            with self.assertRaises(SystemExit) as system_exit:
                main()
            self.assertEqual(0, system_exit.exception.code)

    @pytest.mark.usefixtures("temp_directories")  # type: ignore[misc]
    def test_failing_full_run(self) -> None:
        """Test a failing full run with all flags set.

        A call to extract_implicit_concepts is skipped here.
        This means there are missing relations beetween variables.csv/questions.csv
        and concepts.csv.
        """
        base_path: Path = self.temp_directories["input_path"]

        arguments = [
            "check_relations.py",
            "-i",
            str(base_path),
            "-r",
            str(base_path.joinpath("relations.json")),
        ]

        with patch.object(sys, "argv", arguments):
            with self.assertRaises(SystemExit) as system_exit:
                main()
            self.assertEqual(1, system_exit.exception.code)

    @pytest.mark.usefixtures("caplog_unittest")  # type: ignore[misc]
    @pytest.mark.usefixtures("temp_directories")  # type: ignore[misc]
    def test_full_run_exceptions(self) -> None:
        """Test a full run with all flags set."""
        base_path: Path = self.temp_directories["input_path"]

        arguments = [
            "check_relations.py",
            "-i",
            str(base_path),
            "-r",
            str(base_path.joinpath("nonexistent_file.json")),
        ]

        with patch.object(sys, "argv", arguments):
            with self.assertRaises(SystemExit) as system_exit:
                main()
            self.assertRegex(
                self.caplog.text,
                f'No.*file.*exist.*{str(base_path.joinpath("nonexistent_file.json"))}',
            )
            self.assertEqual(1, system_exit.exception.code)

        faulty_file = base_path.joinpath("faulty.json")
        with open(faulty_file, "w+", encoding="utf8") as file:
            file.write("{\n")
            file.write('"test": "test"')
        arguments = ["check_relations.py", "-i", str(base_path), "-r", str(faulty_file)]

        with patch.object(sys, "argv", arguments):
            with self.assertRaises(SystemExit) as system_exit:
                main()
            self.assertRegex(self.caplog.text, f".*{str(faulty_file)}:.*line 2 column.*")
            self.assertEqual(1, system_exit.exception.code)


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
