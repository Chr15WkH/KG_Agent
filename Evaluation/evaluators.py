"""Deterministic evaluation for GTSQA entity answers."""

import re
import json
from langfuse import Evaluation
from langfuse.experiment import ExperimentItemResult

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

def experiment_summary_evaluator(
    *,
    item_results: list[ExperimentItemResult],
    execution_records: dict,
    **kwargs,
) -> list[Evaluation]:
    """Summarize an experiment on answerable entity questions."""

    results_by_id = {}
    issues = []

    for result in item_results:
        item_id = result.item.id

        if item_id not in execution_records:
            issues.append(f"Unexpected result: {item_id}")
        elif item_id in results_by_id:
            issues.append(f"Duplicate result: {item_id}")
        else:
            results_by_id[item_id] = result

    # Number of tasks that completed normally
    completed_count = 0
    # Number of tasks that failed during Agent execution
    failed_count = 0
    # Number of items with one valid (exact-match) score
    scored_count = 0
    # Number of items with an exact-match score of 1
    correct_count = 0

    for item_id, record in execution_records.items():
        status = record["execution_status"]
        result = results_by_id.get(item_id)

        if status == "failed":
            failed_count += 1

            if result is not None:
                issues.append(
                    f"Failed task unexpectedly returned a result: {item_id}"
                )

            continue

        if status != "completed":
            issues.append(
                f"Unresolved task: {item_id}, status={status}"
            )
            continue

        completed_count += 1

        if result is None:
            issues.append(f"Missing result: {item_id}")
            continue

        scores = [
            evaluation.value
            for evaluation in result.evaluations
            if evaluation.name == "entity_exact_match"
        ]

        if (
            len(scores) != 1
            or not isinstance(scores[0], (int, float))
            or scores[0] not in (0.0, 1.0)
        ):
            issues.append(
                f"Missing, duplicate, or invalid exact-match score: {item_id}"
            )
            continue

        scored_count += 1
        correct_count += int(scores[0])

    # Total number of dataset items planned for this experiment.
    planned_count = len(execution_records)
    # Whether all planned items were processed without unresolved issues.
    assessment_complete = planned_count > 0 and not issues

    evaluations = [
        Evaluation(name="planned_count", value=planned_count),
        Evaluation(name="completed_count", value=completed_count),
        Evaluation(name="execution_failed_count", value=failed_count),
        Evaluation(name="scored_count", value=scored_count),
        Evaluation(name="correct_count", value=correct_count),
        Evaluation(
            name="assessment_complete",
            value=float(assessment_complete),
            comment=json.dumps(
                {"issues": issues},
                ensure_ascii=False,
            ),
        ),
    ]

    if assessment_complete:
        evaluations.extend(
            [
                Evaluation(
                    name="end_to_end_accuracy",
                    value=correct_count / planned_count,
                    comment=(
                        "Correct answers / all planned items. "
                        "Classified execution failures count as unsuccessful "
                        "attempts. Applies to answerable entity questions."
                    ),
                ),
                Evaluation(
                    name="execution_failure_rate",
                    value=failed_count / planned_count,
                ),
            ]
        )

    return evaluations