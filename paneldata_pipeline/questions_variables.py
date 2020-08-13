from pathlib import Path

from pandas import DataFrame, read_csv


def create_indirect_links_once(df: DataFrame) -> DataFrame:
    """ This function gets a Dataframe as input.

        The function then merges the Dataframe with itself on given keys.
        The function returns the Dataframe with newly added lines
        that result from indirect links.
    """

    # merge the Dataframe with itself based on keys of input study etc. and output study.
    # two rows match if the contents of the left side
    # match the contents of the right side.

    # row 1
    # input_study, input_dataset, input_version, input_variable
    # 1, 1, 1, 1

    # matches row 2
    # output_study, output_dataset, output_version, output_variable
    # 1, 1, 1, 1

    temp = df.merge(
        df,
        right_on=["input_study", "input_dataset", "input_version", "input_variable"],
        left_on=["output_study", "output_dataset", "output_version", "output_variable"],
    )
    wanted_columns = [
        "input_study_x",
        "input_dataset_x",
        "input_version_x",
        "input_variable_x",
        "output_study_y",
        "output_dataset_y",
        "output_version_y",
        "output_variable_y",
    ]
    # select only the columns for
    # input study etc. from the left Dataframe
    # and the output study etc. from the right Dataframe
    temp = temp[wanted_columns]

    # Rename the rows to be of the original format
    rename_columns = {
        "input_study_x": "input_study",
        "input_dataset_x": "input_dataset",
        "input_version_x": "input_version",
        "input_variable_x": "input_variable",
        "output_study_y": "output_study",
        "output_dataset_y": "output_dataset",
        "output_version_y": "output_version",
        "output_variable_y": "output_variable",
    }
    temp.rename(columns=rename_columns, inplace=True)

    # add new rows to the original Dataframe, dropping duplicates
    return df.append(temp).drop_duplicates().reset_index(drop=True)


def create_indirect_links_recursive(df: DataFrame) -> DataFrame:
    """" This function gets a Dataframe as input.

        The function calls create_indirect_links_once()
        until no more new lines are added to the Dataframe.
    """

    df_copy = df.copy()

    # As long as new lines are added to the Dataframe continue looking for indirect links
    while True:
        old_len = len(df_copy)
        df_copy = create_indirect_links_once(df_copy)
        new_len = len(df_copy)
        if old_len == new_len:
            break

    sort_columns = ["input_study", "input_dataset", "input_version", "input_variable"]
    return df_copy.sort_values(by=sort_columns).reset_index(drop=True)


def create_questions_from_generations(
    version: str,
    logical_variables_path: str = "metadata/logical_variables.csv",
    generations_path: str = "metadata/generations.csv",
) -> DataFrame:

    # The file "logical_variables.csv" contains direct links
    # between variables and questions
    # variable1 <relates to> question1

    logical_variables = read_csv(logical_variables_path)
    rename_columns = {
        "study": "study_name",
        "dataset": "dataset_name",
        "variable": "variable_name",
        "questionnaire": "instrument_name",
        "question": "question_name",
    }
    logical_variables.rename(columns=rename_columns, inplace=True)
    logical_variables = logical_variables[rename_columns.values()]

    # There are indirect links between variables and questions
    # if we look into "generations.csv".
    # A variable name can be the output of another variable name,
    # which is related to a question.
    # variable1 <relates to> variable2
    # variable2 <relates to> question1
    # so variable1 relates to question1

    # Read input and output version columns as type "string"
    dtype_settings = {"input_version": str, "output_version": str}
    generations = read_csv(generations_path, dtype=dtype_settings)
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

    wanted_columns = [
        "output_study",
        "output_dataset",
        "output_variable",
        "instrument_name",
        "question_name",
    ]
    indirect_relations = indirect_relations[wanted_columns]

    rename_columns = {
        "output_study": "study_name",
        "output_dataset": "dataset_name",
        "output_variable": "variable_name",
        "questionnaire": "instrument_name",
        "question": "question_name",
    }

    indirect_relations.rename(columns=rename_columns, inplace=True)

    questions_variables = logical_variables.append(indirect_relations)
    questions_variables.dropna(inplace=True)
    questions_variables.drop_duplicates(inplace=True)

    sort_columns = [
        "study_name",
        "dataset_name",
        "variable_name",
        "instrument_name",
        "question_name",
    ]

    questions_variables.sort_values(by=sort_columns, inplace=True)
    return questions_variables.reset_index(drop=True)


def questions_from_generations(version: str, input_folder: Path, output_folder: Path):
    questions_variables = create_questions_from_generations(version)

    # keep only variables from datasets defined in datasets.csv

    datasets = read_csv(input_folder.joinpath("datasets.csv"))
    mask = questions_variables["dataset_name"].isin(datasets["dataset_name"].unique())
    questions_variables = questions_variables[mask]
    questions_variables.to_csv(
        output_folder.joinpath("questions_variables.csv"), index=False
    )
