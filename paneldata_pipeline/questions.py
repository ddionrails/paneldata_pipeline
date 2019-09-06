# -*- coding: utf-8 -*-
"""Preprocess questions and answers."""

from pathlib import Path
from typing import Dict, List

import pandas as pd


def preprocess_item_answers(item_df: pd.DataFrame) -> List[Dict]:
    """Get an item's answers from a dataframe."""
    item_answers = (
        item_df[["value", "label", "label_de"]].dropna().to_dict(orient="records")
    )
    for item_answer in item_answers:
        item_answer["value"] = int(item_answer["value"])
    return item_answers


def preprocess_questions(input_path: Path):  # pylint: disable=too-many-locals
    """Preprocess questions and answers."""

    answers = pd.read_csv(input_path.joinpath("answers.csv"))
    questions = pd.read_csv(input_path.joinpath("questions.csv"))

    # merge questions and answers based on "study", "instrument", "answer_list"
    merged = questions.merge(
        answers, how="outer", on=["study", "instrument", "answer_list"]
    )

    # iterate over instruments
    for (study, instrument), instrument_df in merged.groupby(
        ["study", "instrument"], sort=False
    ):
        # group all questions per instrument in a list
        instrument_question_list = []
        # iterate over questions
        for (question_sort_id, ((_, question), question_df)) in enumerate(
            instrument_df.groupby(["instrument", "name"], sort=False)
        ):
            question_dict = dict(
                study=study,
                instrument=instrument,
                name=question,
                sn=question_sort_id,  # sn: sort_number
                items=[],
            )
            # iterate over questions items
            for (item_sort_id, ((name, text, text_de, scale), item_df)) in enumerate(
                question_df.groupby(["item", "text", "text_de", "scale"], sort=False)
            ):
                if "label" not in question_dict:
                    question_dict["label"] = text
                item_dict = dict(
                    sn=item_sort_id,  # sn: sort_number
                    name=name,
                    text=text,
                    text_de=text_de,
                    scale=scale,
                )
                item_answers = preprocess_item_answers(item_df)
                if item_answers:
                    item_dict["answers"] = item_answers
                question_dict["items"].append(item_dict)
            instrument_question_list.append(question_dict)

        yield (instrument, instrument_question_list)
