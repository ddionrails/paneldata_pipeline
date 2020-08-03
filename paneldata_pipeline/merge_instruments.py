import glob
import json
import os
from collections import OrderedDict
from pathlib import Path
from typing import Dict

import pandas


def read_tables(name):
    tables = glob.glob("metadata/*/*/%s" % name)
    tables += glob.glob("metadata/%s" % name)
    result = pandas.read_csv(tables.pop())
    for table in tables:
        result = result.append(pandas.read_csv(table))
    return result


def import_tables():
    tables = OrderedDict(
        questionnaires=pd.read_csv("metadata/questionnaires.csv"),
        questions=read_tables("questions.csv"),
        answers=read_tables("answers.csv"),
    )
    return tables


def get_answers(tables):
    answers = OrderedDict()
    for i, answer in tables["answers"].iterrows():
        answer = OrderedDict(answer.dropna())
        key = (answer["questionnaire"], answer["answer_list"])
        if not key in answers:
            answers[key] = list()
        _clean_x(answer)
        answers[key].append(answer)
    return answers


def get_instruments(tables):
    instrument_list = [
        OrderedDict(row.dropna()) for i, row in tables["questionnaires"].iterrows()
    ]
    instruments = OrderedDict([(x["questionnaire"], x) for x in instrument_list])
    for instrument in instruments.values():
        instrument["instrument"] = instrument["questionnaire"]
        instrument["questions"] = OrderedDict()
    return instruments


def fill_questions(tables, instruments, answers):
    for _, question_row in tables["questions"].iterrows():
        question_row.dropna(inplace=True)
        instrument_name = question_row["questionnaire"]
        question_name = question_row["question"]
        if "item" in question_row.keys():
            item_name = question_row["item"]
        else:
            item_name = "root"
        if not instrument_name in instruments:
            instruments[instrument_name] = OrderedDict(
                instrument=instrument_name, questions=OrderedDict()
            )
        instrument_questions = instruments[instrument_name]["questions"]
        if not question_name in instrument_questions:
            question = OrderedDict()
            question["question"] = question_name
            question["name"] = question_name
            if not "label" in question and "text" in question_row:
                question["label"] = question_row["text"]
            question["items"] = OrderedDict()
            question["sn"] = len(instrument_questions)
            question["instrument"] = question_row["questionnaire"]
            question["study"] = question_row["study"]
            instrument_questions[question_name] = question
        question_items = instrument_questions[question_name]["items"]
        try:
            key = (question_row["questionnaire"], question_row["answer_list"])
            question_row["answers"] = answers[key]
        except:
            pass
        question_row["sn"] = len(question_items)
        _clean_x(question_row)
        question_items[item_name] = question_row.to_dict()
    for _, instrument in instruments.items():
        for _, question in instrument["questions"].items():
            qitems = question["items"]
            for key, question_row in qitems.items():
                question_row["item"] = str(key)
                question_row["number"] = str(question_row.get("number", ""))
                for k in [k for k in question_row.keys() if "." in k]:
                    question_row.pop(k)
            question["items"] = list(qitems.values())
    return instruments


def _clean_x(x):
    del x["study"]
    del x["questionnaire"]
    if "answer_list" in x and not "question" in x:
        del x["answer_list"]
    if "question" in x:
        del x["question"]
    return x


def write_json(instruments, output_folder: Path):
    if not output_folder.exists():
        os.mkdir(output_folder)

    for instrument_name, instrument in instruments.items():
        with open(output_folder.joinpath(f"{instrument_name}.json"), "w") as f:
            json.dump(instrument, f, indent=2, ensure_ascii=False)


def main(
    input_folder=Path("metadata").absolute(),
    output_folder=Path("ddionrails/instruments").absolute(),
):
    tables = OrderedDict(
        questionnaires=pandas.read_csv(
            input_folder.joinpath("questionnaires.csv"), encoding="utf-8"
        ),
        questions=pandas.read_csv(
            input_folder.joinpath("questions.csv"), encoding="utf-8"
        ),
        answers=pandas.read_csv(input_folder.joinpath("answers.csv"), encoding="utf-8"),
    )

    answers = get_answers(tables)

    instruments = get_instruments(tables)

    fill_questions(tables, instruments, answers)
    for _file in glob.glob(str(output_folder.joinpath("*.json"))):
        os.remove(_file)
    write_json(instruments, output_folder)
    return instruments


if __name__ == "__main__":
    instruments = main(export_yaml=True)
