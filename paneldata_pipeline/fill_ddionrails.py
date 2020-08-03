import pathlib
import shutil
from collections import OrderedDict

import pandas

from merge_instruments import main as merge_instruments
from questions_variables import questions_from_generations
from topics import TopicParser
from transformations import preprocess_transformations

STUDY = "soep-core"
VERSION = "v35"

INPUT_DIRECTORY = pathlib.Path("metadata")
OUTPUT_DIRECTORY = pathlib.Path("ddionrails")


def create_questions_from_generations(
    version: str,
    logical_variables_path: str = "metadata/logical_variables.csv",
    generations_path: str = "metadata/generations.csv",
) -> pd.DataFrame:

    # The file "logical_variables.csv" contains direct links between variables and questions
    # variable1 <relates to> question1

    logical_variables = pd.read_csv(logical_variables_path)
    RENAME_COLUMNS = {
        "study": "study_name",
        "dataset": "dataset_name",
        "variable": "variable_name",
        "questionnaire": "instrument_name",
        "question": "question_name",
    }
    logical_variables.rename(columns=RENAME_COLUMNS, inplace=True)
    logical_variables = logical_variables[RENAME_COLUMNS.values()]

    # There are indirect links between variables and questions if we look into "generations.csv".
    # A variable name can be the output of another variable name, which is related to a question.
    # variable1 <relates to> variable2
    # variable2 <relates to> question1
    # so variable1 relates to question1

    # Read input and output version columns as type "string"
    DTYPE_SETTINGS = {"input_version": str, "output_version": str}
    generations = pd.read_csv(generations_path, dtype=DTYPE_SETTINGS)
    updated_generations = create_indirect_links_recursive(generations)

    # Remove rows when output version is not the specified version
    updated_generations = updated_generations[
        updated_generations["output_version"] == version
    ]

    indirect_relations = updated_generations.merge(
        logical_variables,
        left_on=("input_dataset", "input_variable"),
        right_on=("dataset_name", "variable_name"),
    )

    WANTED_COLUMNS = [
        "output_study",
        "output_dataset",
        "output_variable",
        "instrument_name",
        "question_name",
    ]
    indirect_relations = indirect_relations[WANTED_COLUMNS]

    RENAME_COLUMNS = {
        "output_study": "study_name",
        "output_dataset": "dataset_name",
        "output_variable": "variable_name",
        "questionnaire": "instrument_name",
        "question": "question_name",
    }

    indirect_relations.rename(columns=RENAME_COLUMNS, inplace=True)

    questions_variables = logical_variables.append(indirect_relations)
    questions_variables.dropna(inplace=True)
    questions_variables.drop_duplicates(inplace=True)

    SORT_COLUMNS = [
        "study_name",
        "dataset_name",
        "variable_name",
        "instrument_name",
        "question_name",
    ]

    questions_variables.sort_values(by=SORT_COLUMNS, inplace=True)
    return questions_variables.reset_index(drop=True)


def concepts():
    _concepts = pandas.read_csv("metadata/concepts.csv")
    _concepts.rename(
        columns={"concept": "name", "topic_prefix": "topic_name"}, inplace=True
    )
    _concepts.drop_duplicates("name")
    _concepts.to_csv("ddionrails/concepts.csv", index=False)


def main():
    questions_from_generations(VERSION)
    merge_instruments()
    TopicParser(
        topics_input_csv="ddionrails/topics.csv",
        concepts_input_csv="ddionrails/concepts.csv",
    ).to_json()
    transformations = preprocess_transformations(
        INPUT_DIRECTORY.joinpath("generations.csv"), STUDY, VERSION
    )
    transformations.to_csv(OUTPUT_DIRECTORY.joinpath("transformations.csv"), index=False)


if __name__ == "__main__":
    main()
