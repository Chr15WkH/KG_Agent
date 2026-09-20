"""Deterministic evaluation for GTSQA entity answers."""

import re
import json
from langfuse import Evaluation

def normalize_entity_answers(
    answers: list[str] | None,
) -> list[str] | None:
    """Convert QIDs or 'label (QID)' strings to unique sorted QIDs."""
    if answers is None:
        return None

    if not isinstance(answers, list):
        raise ValueError("Entity answers must be a list or None.")

    normalized = set()

    for answer in answers:
        if not isinstance(answer, str):
            raise ValueError("Each entity answer must be a string.")

        text = answer.strip()

        if re.fullmatch(r"Q[1-9]\d*", text):
            qid = text
        else:
            match = re.fullmatch(r".+\((Q[1-9]\d*)\)", text)

            if match is None:
                raise ValueError(
                    f"Cannot extract a QID from answer: {answer!r}"
                )

            qid = match.group(1)

        normalized.add(qid)

    return sorted(normalized)


def evaluate_entity_exact_match(
    answer_payload: list[str] | None,
    gold_answer: list[str],
) -> dict:
    """Score exact entity-set equality for answerable GTSQA items."""
    # Invalid Gold is a data error, not an Agent error.
    normalized_gold = normalize_entity_answers(gold_answer)

    if normalized_gold is None:
        raise ValueError("Gold answer must be a list, not None.")

    try:
        predicted_answer = normalize_entity_answers(answer_payload)
    except ValueError as error:
        return {
            "predicted_answer": None,
            "gold_answer": normalized_gold,
            "normalization_status": "failed",
            "normalization_error": str(error),
            "entity_exact_match": 0.0,
        }

    correct = (
        predicted_answer is not None
        and predicted_answer == normalized_gold
    )

    return {
        "predicted_answer": predicted_answer,
        "gold_answer": normalized_gold,
        "normalization_status": (
            "no_answer" if predicted_answer is None else "success"
        ),
        "normalization_error": None,
        "entity_exact_match": float(correct),
    }

def entity_exact_match_evaluator(
    *,
    output,
    expected_output,
    **kwargs,
) -> Evaluation:
    """Adapt the existing scoring function to Langfuse experiments."""
    if not isinstance(output, dict) or "answer_payload" not in output:
        raise ValueError(
            "Task output must contain 'answer_payload'."
        )

    evaluation = evaluate_entity_exact_match(
        answer_payload=output["answer_payload"],
        gold_answer=expected_output,
    )

    return Evaluation(
        name="entity_exact_match",
        value=evaluation["entity_exact_match"],
        comment=json.dumps(
            {
                "predicted_answer": evaluation["predicted_answer"],
                "gold_answer": evaluation["gold_answer"],
                "normalization_status": evaluation["normalization_status"],
                "normalization_error": evaluation["normalization_error"],
            },
            ensure_ascii=False,
        ),
    )