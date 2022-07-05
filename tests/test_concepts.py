""" Tests for the paneldata_pipeline.concepts module."""
import csv
import unittest
from os import remove
from pathlib import Path
from typing import Dict

import pytest

from paneldata_pipeline.concepts import extract_implicit_concepts


@pytest.mark.usefixtures("temp_directories")
class TestExtractImplicitConcepts(unittest.TestCase):
    """Test the extraction of concepts only present in variables and question data"""

    concepts_path: Path
    questions_path: Path
    variables_path: Path
    temp_directories: Dict[str, Path]

    def test_extract_implicit_concept(self) -> None:
        """Are the implicit concepts added to the concepts.csv?"""
        with open(self.concepts_path, "r", encoding="utf8") as csv_file:
            concept_names = {row["name"] for row in csv.DictReader(csv_file)}
        with open(self.variables_path, "r", encoding="utf8") as csv_file:
            implicit_concept_names = {row["concept"] for row in csv.DictReader(csv_file)}
        with open(self.questions_path, "r", encoding="utf8") as csv_file:
            implicit_concept_names.update(
                {row["concept"] for row in csv.DictReader(csv_file)}
            )

        self.assertLess(len(concept_names), len(implicit_concept_names))

        extract_implicit_concepts(
            input_path=self.temp_directories["input_path"],
            concepts_path=self.concepts_path,
            output_concepts_path=self.concepts_path,
        )

        with open(self.concepts_path, "r", encoding="utf8") as csv_file:
            concept_names = {row["name"] for row in csv.DictReader(csv_file)}

        self.assertSetEqual(implicit_concept_names, concept_names)

    def test_extract_implicit_concept_without_concepts_path(self) -> None:
        """Does the `concepts_path` argument have the correct default value?"""
        with open(self.concepts_path, "r", encoding="utf8") as csv_file:
            concept_names = {row["name"] for row in csv.DictReader(csv_file)}
        with open(self.variables_path, "r", encoding="utf8") as csv_file:
            implicit_concept_names = {row["concept"] for row in csv.DictReader(csv_file)}
        with open(self.questions_path, "r", encoding="utf8") as csv_file:
            implicit_concept_names.update(
                {row["concept"] for row in csv.DictReader(csv_file)}
            )

        self.assertLess(len(concept_names), len(implicit_concept_names))

        extract_implicit_concepts(input_path=self.temp_directories["input_path"])

        with open(self.concepts_path, "r", encoding="utf8") as csv_file:
            concept_names = {row["name"] for row in csv.DictReader(csv_file)}

        self.assertSetEqual(implicit_concept_names, concept_names)

    def test_variable_import_without_concept_csv(self) -> None:
        """Is a concepts.csv added if it did not exist?"""

        remove(self.concepts_path)

        with open(self.variables_path, "r", encoding="utf8") as csv_file:
            implicit_concept_names = {row["concept"] for row in csv.DictReader(csv_file)}
        with open(self.questions_path, "r", encoding="utf8") as csv_file:
            implicit_concept_names.update(
                {row["concept"] for row in csv.DictReader(csv_file)}
            )

        extract_implicit_concepts(
            input_path=self.temp_directories["input_path"],
            concepts_path=self.concepts_path,
        )

        with open(self.concepts_path, "r", encoding="utf8") as csv_file:
            dict_reader = csv.DictReader(csv_file)
            if dict_reader.fieldnames:
                concept_file_header = list(dict_reader.fieldnames)
            concept_names = {row["name"] for row in dict_reader}

        self.assertSetEqual(implicit_concept_names, concept_names)
        self.assertListEqual(
            [
                "study",
                "name",
                "label",
                "label_de",
                "description",
                "description_de",
                "topic",
            ],
            concept_file_header,
        )
