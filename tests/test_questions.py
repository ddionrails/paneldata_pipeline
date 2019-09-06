# -*- coding: utf-8 -*-
"""Test cases for preprocessing of questions and answers."""

import json
from pathlib import Path

from paneldata_pipeline.questions import preprocess_questions


def test_preprocess_questions():
    """Test preprocessing of questions and answers data in tests/test_data"""
    # all instruments are stored in "result"
    result = [
        instrument[1] for instrument in preprocess_questions(Path("tests/test_data"))
    ]
    with open("tests/test_data/expected.json", "r") as infile:
        expected = json.load(infile)
    # compare one instrument to the stored instance from JSON file
    assert result[0] == expected
