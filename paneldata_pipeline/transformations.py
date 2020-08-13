# -*- coding: utf-8 -*-

""" Preprocessing step for transformations """

from collections import OrderedDict
from pathlib import Path
from typing import Optional

from pandas import DataFrame, read_csv

from paneldata_pipeline.questions_variables import create_indirect_links_recursive


def preprocess_transformations(
    study: str,
    version: str,
    input_folder: Optional[Path] = None,
    output_folder: Optional[Path] = None,
    verbose: bool = False,
) -> DataFrame:

    if not input_folder:
        input_folder = Path("ddionrails/").resolve()

    # load variables for filtering
    variables = read_csv(input_folder.joinpath("variables.csv"))
    variables["compare"] = variables["dataset_name"].astype(str) + variables[
        "variable_name"
    ].astype(str)

    columns = OrderedDict(
        [
            ("input_study", "origin_study_name"),
            ("input_dataset", "origin_dataset_name"),
            ("input_variable", "origin_variable_name"),
            ("output_study", "target_study_name"),
            ("output_dataset", "target_dataset_name"),
            ("output_variable", "target_variable_name"),
        ]
    )
    dtype_settings = {"input_version": str, "output_version": str}
    generations = read_csv(input_folder.joinpath("generations.csv"), dtype=dtype_settings)
    if verbose:
        print(generations.shape)
        print(generations.head())

    # remove rows without the given version as "output_version"
    filtered_generations = generations[
        (generations["output_version"] == version)
        & (generations["input_version"] == version)
    ]
    if verbose:
        print(filtered_generations.shape)
        print(filtered_generations.head())

    # follow transitive relations in the generations file
    generations_with_indirect_links = create_indirect_links_recursive(
        filtered_generations
    )
    if verbose:
        print(generations_with_indirect_links.shape)
        print(generations_with_indirect_links.head())

    # remove "input_version" and "output_version" columns
    generations_with_indirect_links.drop(
        ["input_version", "output_version"], axis=1, inplace=True
    )

    # drop duplicates, without versions left and right, there are lots of duplicated rows
    generations_with_indirect_links.drop_duplicates(inplace=True)
    if verbose:
        print(generations_with_indirect_links.shape)
        print(generations_with_indirect_links.head())

    # remove rows with the "wrong" input or output study
    input_mask = generations_with_indirect_links["input_study"] == study
    output_mask = generations_with_indirect_links["output_study"] == study
    generations_with_indirect_links = generations_with_indirect_links[
        input_mask & output_mask
    ]
    if verbose:
        print(generations_with_indirect_links.shape)
        print(generations_with_indirect_links.head())

    # remove rows, where left and right side of dataframe are the same variable
    # (due to removing versions)
    mask = (
        generations_with_indirect_links["input_dataset"]
        != generations_with_indirect_links["output_dataset"]
    ) | (
        generations_with_indirect_links["input_variable"]
        != generations_with_indirect_links["output_variable"]
    )
    transformations = generations_with_indirect_links[mask]
    if verbose:
        print(generations_with_indirect_links.shape)
        print(generations_with_indirect_links.head())

    # remove rows where input dataset and variable are not defined in variables.csv
    transformations["compare"] = transformations["input_dataset"].astype(
        str
    ) + transformations["input_variable"].astype(str)
    transformations = transformations[
        transformations["compare"].isin(variables["compare"])
    ]

    transformations["compare"] = transformations["output_dataset"].astype(
        str
    ) + transformations["output_variable"].astype(str)
    transformations = transformations[
        transformations["compare"].isin(variables["compare"])
    ]
    # drop helper column
    transformations.drop("compare", 1, inplace=True)
    if verbose:
        print(generations_with_indirect_links.shape)
        print(generations_with_indirect_links.head())
    transformations.rename(columns=columns, inplace=True)
    transformations.to_csv(output_folder.joinpath("transformations.csv"), index=False)
