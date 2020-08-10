""" Tests for the paneldata_pipeline.concepts module."""
import csv
import unittest
from os import remove
from pathlib import Path
from shutil import copy, rmtree
from tempfile import mkdtemp

from paneldata_pipeline.concepts import extract_implicit_concepts


class TestExtractImplicitConcepts(unittest.TestCase):
    """ Test the extraction of concepts only present in the variables.csv"""

    def setUp(self):
        self.sandbox_directory = Path(mkdtemp()).absolute()
        data_path = Path("./tests/test_data/").absolute()
        copy(data_path.joinpath("concepts.csv"), self.sandbox_directory)
        copy(data_path.joinpath("variables.csv"), self.sandbox_directory)
        self.concepts_path = self.sandbox_directory.joinpath("concepts.csv")
        self.variables_path = self.sandbox_directory.joinpath("variables.csv")

        return super().setUp()

    def test_variable_import_with_orphaned_concept(self):
        """Are the concepts from the variables.csv added to the concepts.csv?"""
        with open(self.concepts_path, "r") as csv_file:
            concept_names = {row["name"] for row in csv.DictReader(csv_file)}
        with open(self.variables_path, "r") as csv_file:
            variable_concept_names = {row["concept"] for row in csv.DictReader(csv_file)}
        self.assertLess(len(concept_names), len(variable_concept_names))

        extract_implicit_concepts(self.concepts_path, self.variables_path)

        with open(self.concepts_path, "r") as csv_file:
            concept_names = {row["name"] for row in csv.DictReader(csv_file)}

        self.assertSetEqual(variable_concept_names, concept_names)

    def test_variable_import_without_concept_csv(self):
        """Is a concepts.csv added if it did not exist?"""

        remove(self.concepts_path)

        with open(self.variables_path, "r") as csv_file:
            variable_concept_names = {row["concept"] for row in csv.DictReader(csv_file)}

        extract_implicit_concepts(self.concepts_path, self.variables_path)

        with open(self.concepts_path, "r") as csv_file:
            dict_reader = csv.DictReader(csv_file)
            concept_file_header = dict_reader.fieldnames
            concept_names = {row["name"] for row in dict_reader}

        self.assertSetEqual(variable_concept_names, concept_names)
        self.assertListEqual(["name", "topic", "label_de", "label"], concept_file_header)

    def tearDown(self):
        rmtree(self.sandbox_directory)
        return super().tearDown()
