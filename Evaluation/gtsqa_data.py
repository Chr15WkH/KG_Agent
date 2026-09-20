import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

def load_sample(sample_id: int) -> dict:
    """Load one raw GTSQA sample without converting its graph."""
    input_path = PROJECT_ROOT / "Dataset" / "gtsqa_development_agent_input.jsonl"

    with input_path.open("r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue

            sample = json.loads(line)

            if str(sample["id"]) == str(sample_id):
                return sample

    raise ValueError(f"GTSQA sample {sample_id} was not found.")

def load_gold(sample_id: int) -> dict:
    """Load evaluation-only reference data for one sample."""
    gold_path = PROJECT_ROOT / "Dataset" / "gtsqa_development_gold.json"

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
    }