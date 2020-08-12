"""Tests for the merge_instruments Module."""
import json
import unittest
from pathlib import Path
from shutil import rmtree
from tempfile import mkdtemp

from paneldata_pipeline.merge_instruments import merge_instruments


class TestMergeInstruments(unittest.TestCase):
    """Tests for the correction creation of instrument JSON files"""

    def setUp(self) -> None:
        self.in_dir = Path("./tests/test_data/").absolute()
        self.out_dir = Path(mkdtemp()).absolute()
        with open(
            Path("./tests/test_data/expected/some-questionnaire.json").absolute(), "r"
        ) as _file:
            self.expected_dataset = json.load(_file)

        return super().setUp()

    def test_complete(self) -> None:
        """Test the creation precess in its entirety"""
        merge_instruments(input_folder=self.in_dir, output_folder=self.out_dir)
        with open(self.out_dir.joinpath("some-questionnaire.json"), "r") as _file:
            result = json.load(_file)
        self.assertDictEqual(self.expected_dataset, result)

    def tearDown(self) -> None:
        rmtree(self.out_dir)
        return super().tearDown()
