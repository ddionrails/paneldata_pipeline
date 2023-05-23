"""Provides the functionality to create a topic tree JSON file."""
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, TypedDict, Union

import pandas

LANGUAGES = {"en": "", "de": "_de"}


class LeafNode(TypedDict):
    """A Node referencing a Concept"""

    title: str
    key: str
    type: str


class Node(LeafNode):
    """A Node referencing a Topic"""

    children: List[Any]


class Topic:
    all_objects: List[Any] = []

    def __init__(
        self, name: str = "", parent_name: Optional[str] = None, label: str = ""
    ):
        self.name = name
        self.parent_name = parent_name
        self.label = label if str(label) != "nan" else ""
        self.children: List[Topic] = []
        self.concepts: List[Concept] = []
        self.all_objects.append(self)

    def to_dict(self) -> Node:
        children: List[Union[Node, LeafNode]] = [x.to_dict() for x in self.children]
        children += [x.to_dict() for x in self.concepts]
        return {
            "title": self.label,
            "key": f"topic_{self.name}",
            "type": "topic",
            "children": children,
        }

    @classmethod
    def get_by_name(cls, name: Optional[str]) -> Optional[Any]:
        """Get topic from all_objects by name"""
        if name is None:
            return None
        for topic in cls.all_objects:
            if topic.name == name:
                return topic
        return None

    @classmethod
    def get_root_topics(cls) -> List[Any]:
        """Return topics with no parents (== root topics)"""
        return [x for x in cls.all_objects if x.parent_name is None]

    @classmethod
    def add_topics_to_parents(cls) -> None:
        for topic in cls.all_objects:
            parent = Topic.get_by_name(topic.parent_name)
            if parent:
                parent.children.append(topic)


class Concept:
    all_objects: List[Any] = []

    def __init__(self, name: str, topic_name: str, label: str):
        self.name = name
        self.topic_name = topic_name
        self.label = label if str(label) != "nan" else ""
        self.all_objects.append(self)

    def to_dict(self) -> LeafNode:
        return {"title": self.label, "key": f"concept_{self.name}", "type": "concept"}

    @classmethod
    def add_concepts_to_topics(cls) -> None:
        for concept in cls.all_objects:
            topic = Topic.get_by_name(concept.topic_name)
            if topic:
                topic.concepts.append(concept)
            else:
                print(f"Topic not found: {concept.topic_name}")


class TopicParser:
    """
    Generate ``topics.json`` from ``topics.csv`` and ``concepts.csv``::

        TopicParser().to_json()
    """

    def __init__(
        self,
        input_folder: Path,
        output_folder: Path,
        languages: Optional[List[str]] = None,
    ):
        topics_input_csv = input_folder.joinpath("topics.csv")
        concepts_input_csv = input_folder.joinpath("concepts.csv")
        self.output_json = output_folder.joinpath("topics.json")
        if not languages:
            languages = ["en", "de"]
        self.topics_input_csv = topics_input_csv
        self.concepts_input_csv = concepts_input_csv
        self.topics_data = pandas.read_csv(topics_input_csv)
        self.concepts_data = pandas.read_csv(concepts_input_csv)
        self.languages = languages

    def to_json(self) -> None:
        json_dict = self._create_json()
        with open(self.output_json, "w", encoding="utf8") as json_file:
            json_file.write(json.dumps(json_dict))

    def _create_json(self) -> List[Dict[str, Any]]:
        result = []
        for language in self.languages:
            result.append({"language": language, "topics": self.to_dict(language)})
        return result

    def to_dict(self, language: str) -> List[Node]:
        for row in self.topics_data.to_dict("records"):
            if str(row.get("parent")) == "nan":
                parent_name = None
            else:
                parent_name = row.get("parent")
            label = row.get("label" + LANGUAGES[language])
            if label in ["nan", ""] or not label:
                label = row.get("name")
            Topic(
                name=row.get("name"),
                label=label,
                parent_name=parent_name,
            )
        for row in self.concepts_data.to_dict("records"):
            if str(row.get("name", "nan")) != "nan":
                Concept(
                    name=row.get("name"),
                    topic_name=row.get("topic"),
                    label=row.get("label" + LANGUAGES[language], row.get("name")),
                )
        Topic.add_topics_to_parents()
        Concept.add_concepts_to_topics()
        print(f"Language: {language}")
        print(f"Topics: {len(Topic.all_objects)}")
        print(f"Concepts: {len(Concept.all_objects)}")
        result = [topic.to_dict() for topic in Topic.get_root_topics()]
        Topic.all_objects = []
        Concept.all_objects = []
        return result
