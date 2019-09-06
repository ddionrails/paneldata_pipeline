# -*- coding: utf-8 -*-
# pylint: disable=protected-access
"""Test cases for preprocessing of topics."""

import json
from pathlib import Path

from paneldata_pipeline.topics import TopicParser


def test_topicparser():
    """Test TopicParser can merge concepts and topics into JSON topiclist."""
    path = Path("tests/test_data")
    result = TopicParser(
        path.joinpath("topics.csv"), path.joinpath("concepts.csv")
    )._create_json()
    with open("tests/expected/topics.json", "r") as infile:
        expected = json.load(infile)
    assert expected == result
