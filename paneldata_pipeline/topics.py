# -*- coding: utf-8 -*-

""" TopicParser from
<https://github.com/ddionrails/ddi.py/blob/master/ddi/onrails/repos/topics.py>
Copyright (c) 2018, DIW
Author: 2018, Marcel Hebing
"""

import json
import os

import pandas as pd

LANGUAGES = dict(en="", de="_de")


class Topic:

    all_objects = []

    def __init__(self, name=None, parent_name=None, label=None):
        self.name = name
        self.parent_name = parent_name
        self.label = label if str(label) != "nan" else ""
        self.children = []
        self.concepts = []
        self.all_objects.append(self)

    def to_dict(self):
        children = [x.to_dict() for x in self.children]
        children += [x.to_dict() for x in self.concepts]
        return dict(
            title=self.label, key="topic_%s" % self.name, type="topic", children=children
        )

    @classmethod
    def get_by_name(cls, name):
        """Get topic from all_objects by name"""
        try:
            return [x for x in cls.all_objects if x.name == name][0]
        except:
            return None

    @classmethod
    def get_root_topics(cls):
        """Return topics with no parents (== root topics)"""
        return [x for x in cls.all_objects if x.parent_name == None]

    @classmethod
    def add_topics_to_parents(cls):
        for topic in cls.all_objects:
            try:
                parent = Topic.get_by_name(topic.parent_name)
                parent.children.append(topic)
            except:
                pass


class Concept:

    all_objects = []

    def __init__(self, name=None, topic_name=None, label=None):
        self.name = name
        self.topic_name = topic_name
        self.label = label if str(label) != "nan" else ""
        self.all_objects.append(self)

    def to_dict(self):
        return dict(title=self.label, key="concept_%s" % self.name, type="concept")

    @classmethod
    def add_concepts_to_topics(cls):
        for concept in cls.all_objects:
            topic = Topic.get_by_name(concept.topic_name)
            if topic:
                topic.concepts.append(concept)
            else:
                print("Topic not found: %s" % concept.topic_name)


class TopicParser:
    """
    Generate ``topics.json`` from ``topics.csv`` and ``concepts.csv``::

        TopicParser().to_json()
    """

    def __init__(
        self,
        topics_input_csv="metadata/topics.csv",
        concepts_input_csv="metadata/concepts.csv",
        languages=["en", "de"],
    ):
        self.topics_input_csv = topics_input_csv
        self.concepts_input_csv = concepts_input_csv
        self.topics_data = pd.read_csv(topics_input_csv)
        self.concepts_data = pd.read_csv(concepts_input_csv)
        self.languages = languages

    def to_csv(self, topics_output_csv="ddionrails/topics.csv"):
        os.system("cp %s %s" % (self.topics_input_csv, topics_output_csv))

    def to_json(self, topics_output_json="ddionrails/topics.json"):
        json_dict = self._create_json()
        with open(topics_output_json, "w") as f:
            f.write(json.dumps(json_dict))

    def _create_json(self):
        result = []
        for language in self.languages:
            result.append(dict(language=language, topics=self._convert_to_dict(language)))
        return result

    def _convert_to_dict(self, language):
        for row in self.topics_data.to_dict("records"):
            if str(row.get("parent")) == "nan":
                parent_name = None
            else:
                parent_name = row.get("parent")
            Topic(
                name=row.get("name"),
                label=row.get("label" + LANGUAGES[language], row.get("name")),
                parent_name=parent_name,
            )
        for row in self.concepts_data.to_dict("records"):
            if str(row.get("topic", "nan")) != "nan":
                Concept(
                    name=row.get("name"),
                    topic_name=row.get("topic"),
                    label=row.get("label" + LANGUAGES[language], row.get("name")),
                )
        Topic.add_topics_to_parents()
        Concept.add_concepts_to_topics()
        print("Language: %s" % language)
        print("Topics: %s" % len(Topic.all_objects))
        print("Concepts: %s" % len(Concept.all_objects))
        result = [topic.to_dict() for topic in Topic.get_root_topics()]
        Topic.all_objects = []
        Concept.all_objects = []
        return result


if __name__ == "__main__":
    tp = TopicParser()
    tp.to_csv()
    tp.to_json()
