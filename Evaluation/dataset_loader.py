"""Load local dataset samples and evaluation-only Gold records."""

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_DIR = PROJECT_ROOT / "Dataset"


def load_gtsqa_sample(sample_id: int) -> dict:
    """Load one original GTSQA sample without converting its graph."""
    input_path = DATASET_DIR / "gtsqa_development_agent_input.jsonl"

    with input_path.open("r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue

            sample = json.loads(line)

            if str(sample["id"]) == str(sample_id):
                return sample

    raise ValueError(f"GTSQA sample {sample_id} was not found.")


def load_gtsqa_gold(sample_id: int) -> dict:
    """Load the GTSQA reference answer and supporting subgraph for evaluation."""
    gold_path = DATASET_DIR / "gtsqa_development_gold.json"

    with gold_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    matches = [item for item in data["questions"] if str(item["id"]) == str(sample_id)]

    if len(matches) != 1:
        raise ValueError(
            f"Expected exactly one Gold record for sample "
            f"{sample_id}, found {len(matches)}."
        )

    item = matches[0]
    answers = item["evaluation_gold"]["all_answers_wikikg2"]
    supporting_subgraph = item["evaluation_gold"]["full_answer_subgraph_wikikg2"]

    if not isinstance(answers, list) or not all(
        isinstance(answer, str) for answer in answers
    ):
        raise ValueError(
            f"Invalid Gold answer format for sample {sample_id}."
        )

    return {
        "sample_id": str(item["id"]),
        "question": item["question_profile"]["question"],
        "gold_answer": answers,
        "full_answer_subgraph_wikikg2": supporting_subgraph,
    }


def load_gtsqa_ua_gold(sample_id: str) -> dict:
    """Load answerability Ground Truth for a GTSQA_UA variant.

    This function does not reconstruct graphs or execute SPARQL.
    Gold answers and modification records remain in the source file;
    refusal evaluation only requires the question and answerable label.
    """
    if not isinstance(sample_id, str) or not sample_id.strip():
        raise ValueError("GTSQA_UA sample ID must be a non-empty string.")

    gold_path = DATASET_DIR / "gtsqa_ua_gold.json"

    with gold_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    matches = [item for item in data["questions"] if item["id"] == sample_id]

    if len(matches) != 1:
        raise ValueError(
            f"Expected exactly one UA Gold record for sample "
            f"{sample_id}, found {len(matches)}."
        )

    item = matches[0]
    question = item.get("question")
    answerable = item.get("answerable")
    validation = item.get("validation")

    if not isinstance(question, str) or not question.strip():
        raise ValueError(
            f"Invalid question for UA sample {sample_id}."
        )

    if type(answerable) is not bool:
        raise ValueError(
            f"'answerable' must be a Boolean for UA sample {sample_id}."
        )

    if (
        not isinstance(validation, dict)
        or validation.get("status") != "passed"
    ):
        raise ValueError(
            f"UA sample {sample_id} has not passed construction validation."
        )

    return {
        "sample_id": item["id"],
        "question": question,
        "answerable": answerable,
    }