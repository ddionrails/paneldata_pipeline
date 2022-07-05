""" Data manipulation functionality related to the concepts.csv."""
import csv
from pathlib import Path
from typing import Dict, List, Sequence, Set, Tuple


def extract_implicit_concepts(
    input_path: Path, concepts_path: Path = Path(), output_concepts_path: Path = Path()
) -> None:
    """Add missing concepts, only in variables and questions data, to concepts.csv"""
    if concepts_path == Path():
        concepts_path = input_path.joinpath("concepts.csv")
    if output_concepts_path == Path():
        output_concepts_path = input_path.joinpath("concepts.csv")

    implicit_concepts: Dict[str, str] = {}

    for path in [
        input_path.joinpath("variables.csv"),
        input_path.joinpath("questions.csv"),
    ]:
        with open(path, "r", encoding="utf8") as csv_file:
            for row in csv.DictReader(csv_file):
                _concept = row.get("concept", row.get("concept_name"))
                if _concept is None:
                    raise EnvironmentError(
                        f"{concepts_path} is missing the 'concept' field."
                    )
                implicit_concepts[_concept] = row.get("study", row.get("study_name", ""))
                if implicit_concepts[_concept] == "":
                    raise EnvironmentError(
                        f"{concepts_path} is missing the 'study' field."
                    )

    if not concepts_path.exists():
        with open(concepts_path, "w+", encoding="utf8") as concepts_csv:
            csv.DictWriter(
                concepts_csv,
                fieldnames=[
                    "study",
                    "name",
                    "label",
                    "label_de",
                    "description",
                    "description_de",
                    "topic",
                ],
            ).writeheader()

    concept_csv_content, explicit_concepts, concept_fields = __read_explicit_concepts(
        concepts_path
    )

    implicit_concepts = {
        key: value
        for key, value in implicit_concepts.items()
        if key not in explicit_concepts
    }
    implicit_concepts.pop("", None)

    with open(output_concepts_path, "w", encoding="utf8") as concepts_csv:
        writer = csv.DictWriter(concepts_csv, concept_fields, restval="")
        writer.writeheader()
        for row in concept_csv_content:
            writer.writerow(row)
        for concept, study in implicit_concepts.items():
            writer.writerow({"name": concept, "study": study})


def __read_explicit_concepts(
    concepts_path: Path,
) -> Tuple[List[Dict[str, str]], Set[str], Sequence[str]]:
    """Read content, concepts and fieldnames defined in source concepts.csv."""
    with open(concepts_path, "r", encoding="utf8") as concepts_csv:
        concepts_reader = csv.DictReader(concepts_csv)
        concept_csv_content = []
        explicit_concepts = set()
        if concepts_reader.fieldnames:
            concept_fields = concepts_reader.fieldnames
        else:
            raise EnvironmentError(f"{concepts_path} is not a correct concept CSV file.")
        for row in concepts_reader:
            concept_csv_content.append(row)
            explicit_concepts.add(row["name"])

    return (concept_csv_content, explicit_concepts, concept_fields)
