""" Data manipulation functionality related to the concepts.csv."""
import csv
from pathlib import Path


def extract_implicit_concepts(concepts_path: Path, variables_path: Path):
    """Add missing concepts, only present in the variable.csv, to the concepts.csv"""
    with open(variables_path, "r") as variable_csv:
        variable_concepts = {
            row.get("concept", row.get("concept_name"))
            for row in csv.DictReader(variable_csv)
        }

    if not concepts_path.exists():
        default_fields = ["name", "topic", "label_de", "label"]
        with open(concepts_path, "w+") as concepts_csv:
            dict_writer = csv.DictWriter(concepts_csv, fieldnames=default_fields)
            dict_writer.writeheader()

    with open(concepts_path, "r") as concepts_csv:
        _reader = csv.DictReader(concepts_csv)
        concept_csv_content = list(_reader)
        concept_fields = {field: "" for field in _reader.fieldnames}
        concepts = {row["name"] for row in concept_csv_content}
    orphaned_concepts = variable_concepts.difference(concepts)
    if "" in orphaned_concepts:
        orphaned_concepts.remove("")
    with open(concepts_path, "w") as concepts_csv:
        writer = csv.DictWriter(concepts_csv, concept_fields.keys())
        writer.writeheader()
        for row in concept_csv_content:
            writer.writerow(row)
        for concept in orphaned_concepts:
            concept_fields["name"] = concept
            writer.writerow(concept_fields)
