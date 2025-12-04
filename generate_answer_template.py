#!/usr/bin/env python3
"""
Generate a placeholder answer file that matches the expected auto-grader format.

Replace the placeholder logic inside `build_answers()` with your own agent loop
before submitting so the ``output`` fields contain your real predictions.

Reads the input questions from cse_476_final_project_test_data.json and writes
an answers JSON file where each entry contains a string under the "output" key.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List
from agent import query_agent, classify_domain, Domain
import sys
from pathlib import Path
import random


if len(sys.argv) != 6:

    INPUT_PATH = Path("cse_476_final_project_test_data.json")
    OUTPUT_PATH = Path("cse_476_final_project_answers.json")

    EVAL = False
    CLASSIFICATION = False

else:
    INPUT_PATH = Path(sys.argv[1])
    OUTPUT_PATH = Path("cse_476_final_project_answers.json")

    EVAL = (sys.argv[3]) == "True"
    CLASSIFICATION = (sys.argv[5])== "True"

print("running on", INPUT_PATH)


def load_questions(path: Path) -> List[Dict[str, Any]]:
    with path.open("r", encoding="utf-8") as fp:
        data = json.load(fp)
    if not isinstance(data, list):
        raise ValueError("Input file must contain a list of question objects.")

    #for testing | for entire 'return data'
    #return random.sample(data, 100)
    return data


def build_answers(questions: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    answers = []
    for idx, question in enumerate(questions, start=1):
        agent_ans = query_agent(question["input"], classify_domain(question["input"]))
        answers.append({"output": agent_ans})
    return answers

def classify(questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    answers = []
    for idx, question in enumerate(questions, start=1):
        agent_ans = classify_domain(question["input"])
        answers.append({"output": agent_ans})
    return answers

def validate_results(
    questions: List[Dict[str, Any]], answers: List[Dict[str, Any]]
) -> None:
    if len(questions) != len(answers):
        raise ValueError(
            f"Mismatched lengths: {len(questions)} questions vs {len(answers)} answers."
        )
    for idx, answer in enumerate(answers):
        if "output" not in answer:
            raise ValueError(f"Missing 'output' field for answer index {idx}.")
        if not isinstance(answer["output"], str):
            raise TypeError(
                f"Answer at index {idx} has non-string output: {type(answer['output'])}"
            )
        if len(answer["output"]) >= 5000:
            raise ValueError(
                f"Answer at index {idx} exceeds 5000 characters "
                f"({len(answer['output'])} chars). Please make sure your answer does not include any intermediate results."
            )


def main() -> None:
    questions = load_questions(INPUT_PATH)
    answers = build_answers(questions)

    with OUTPUT_PATH.open("w", encoding="utf-8") as fp:
        json.dump(answers, fp, ensure_ascii=False, indent=2)

    with OUTPUT_PATH.open("r", encoding="utf-8") as fp:
        saved_answers = json.load(fp)

    validate_results(questions, saved_answers)
    print(
        f"Wrote {len(answers)} answers to {OUTPUT_PATH} "
        "and validated format successfully."
    )

    if EVAL:
        num_cases = len(questions)
        correct = 0

        for q, ans in zip(questions, answers):
            gt = q["output"]
            pred = ans["output"]

            if pred == gt:
                correct += 1

        acc = correct / num_cases
        print("-----------------PERF------------------")
        print("acc", acc)


    if CLASSIFICATION:
        print("-----------------CLASSIFIER------------------")
        num_cases = len(questions)
        correct = 0

        classifications = classify(questions)
        for q, ans in zip(questions, classifications):
            gt = Domain(q["domain"])
            pred = ans["output"]
            if pred == gt:
                correct += 1
            else:
                print("WRONG-------")
                print(q)
                print("pred", pred)
        acc = correct / num_cases

        print("acc", acc)

if __name__ == "__main__":
    main()

