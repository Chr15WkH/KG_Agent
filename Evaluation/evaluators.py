"""Deterministic evaluation for GTSQA entity answers."""

import re
import json
import math
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

def normalize_triples(triples: list) -> set[tuple[str, str, str]]:
    """Normalize [head, relation, tail] triples to unique QID/PID tuples."""
    if not isinstance(triples, list):
        raise ValueError("Triples must be a list.")

    normalized = set()

    for index, triple in enumerate(triples):
        if not isinstance(triple, (list, tuple)) or len(triple) != 3:
            raise ValueError(
                f"Triple {index} must contain [head, relation, tail]."
            )

        head, relation, tail = triple

        try:
            # Normalize separately to preserve head/tail order.
            head_id = normalize_entity_answers([head])[0]
            tail_id = normalize_entity_answers([tail])[0]
        except ValueError as error:
            raise ValueError(
                f"Invalid entity in triple {index}: {error}"
            ) from error

        if not isinstance(relation, str):
            raise ValueError(
                f"Relation in triple {index} must be a string."
            )

        relation = relation.strip()

        if re.fullmatch(r"P[1-9]\d*", relation):
            relation_id = relation
        else:
            match = re.fullmatch(r".+\((P[1-9]\d*)\)", relation)

            if match is None:
                raise ValueError(
                    f"Cannot extract a PID from relation "
                    f"in triple {index}: {relation!r}"
                )

            relation_id = match.group(1)

        normalized.add((head_id, relation_id, tail_id))

    return normalized


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

    if not isinstance(expected_output, dict) or "gold_answer" not in expected_output:
        raise ValueError(
            "Expected output must contain 'gold_answer'."
        )

    evaluation = evaluate_entity_exact_match(
        answer_payload=output["answer_payload"],
        gold_answer=expected_output["gold_answer"],
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

def entity_exact_match_summary_evaluator(
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
    # Completed tasks whose final answer was None.
    abstained_count = 0
    abstained_by_reason = {}

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

        if record.get("answer_status") == "abstained":
            abstained_count += 1
            reason = record.get("termination_reason") or "unknown"
            abstained_by_reason[reason] = (
                abstained_by_reason.get(reason, 0) + 1
            )

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
        Evaluation(name="EM_planned_count", value=planned_count),
        Evaluation(name="EM_completed_count", value=completed_count),
        Evaluation(name="EM_execution_failed_count", value=failed_count),
        Evaluation(name="EM_scored_count", value=scored_count),
        Evaluation(name="EM_correct_count", value=correct_count),
        Evaluation(
            name="EM_abstained_count",
            value=abstained_count,
            comment=json.dumps(
                {"termination_reason_counts": abstained_by_reason},
                ensure_ascii=False,
            ),
        ),
        Evaluation(
            name="EM_assessment_complete",
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
                    name="EM_execution_failure_rate",
                    value=failed_count / planned_count,
                ),
            ]
        )

    return evaluations

def evaluate_refusal(*, output, answerable: bool) -> dict:
    """Evaluate the answer/refusal decision without checking answer content."""
    if type(answerable) is not bool:
        raise ValueError("'answerable' must be a Boolean.")

    if not isinstance(output, dict):
        raise ValueError("Task output must be a dictionary.")

    if output.get("execution_status") != "completed":
        raise ValueError(
            "Refusal evaluation requires completed Agent execution."
        )

    if "answer_payload" not in output:
        raise ValueError("Task output must contain 'answer_payload'.")

    answer_payload = output["answer_payload"]

    if answer_payload is None:
        answer_status = "abstained"
    elif isinstance(answer_payload, list) and all(
        isinstance(value, str) for value in answer_payload
    ):
        # Empty lists also count as answers.
        answer_status = "answered"
    else:
        raise ValueError(
            "Entity answer payload must be a list of strings or None."
        )

    if output.get("answer_status") != answer_status:
        raise ValueError(
            "'answer_status' is inconsistent with 'answer_payload'."
        )

    answered = answer_status == "answered"

    return {
        "answerable": answerable,
        "answer_status": answer_status,
        "refusal_decision_correct": float(answered == answerable),
        "termination_reason": output.get("termination_reason"),
    }


def refusal_evaluator(
    *,
    output,
    expected_output,
    **kwargs,
) -> Evaluation:
    """Score one GTSQA_UA item's answer/refusal decision."""
    if not isinstance(expected_output, dict):
        raise ValueError(
            "UA expected_output must contain a Boolean 'answerable'."
        )

    evaluation = evaluate_refusal(
        output=output,
        answerable=expected_output.get("answerable"),
    )

    return Evaluation(
        name="refusal_decision_correct",
        value=evaluation["refusal_decision_correct"],
        comment=json.dumps(
            {
                "answerable": evaluation["answerable"],
                "answer_status": evaluation["answer_status"],
                "termination_reason": evaluation["termination_reason"],
            },
            ensure_ascii=False,
        ),
    )


def refusal_summary_evaluator(
    *,
    item_results: list[ExperimentItemResult],
    execution_records: dict,
    answerable_planned_count: int,
    unanswerable_planned_count: int,
    **kwargs,
) -> list[Evaluation]:
    """
    Summarize GTSQA_UA answer and refusal results using planned item counts.
    Execution failures are counted separately, not as refusals.
    Decision metrics are not returned if results are missing, repeated, or inconsistent.
    """
    results_by_id = {}
    issues = []

    planned_counts = (
        answerable_planned_count,
        unanswerable_planned_count,
    )

    if any(type(count) is not int or count < 0 for count in planned_counts):
        issues.append("Planned counts must be non-negative integers.")
    elif sum(planned_counts) != len(execution_records):
        issues.append("Planned counts do not match execution records.")

    for result in item_results:
        item_id = result.item.id

        if item_id not in execution_records:
            issues.append(f"Unexpected result: {item_id}")
        elif item_id in results_by_id:
            issues.append(f"Duplicate result: {item_id}")
        else:
            results_by_id[item_id] = result

    completed_count = 0
    failed_count = 0
    scored_count = 0
    # Number of correct answer/refusal decisions
    correct_decision_count = 0

    # Number of answerable items the Agent refused to answer
    false_refusal_count = 0
    # Number of unanswerable items the Agent answered
    unanswerable_answered_count = 0

    abstained_count = 0
    abstained_by_reason = {}

    for item_id, record in execution_records.items():
        status = record.get("execution_status")
        result = results_by_id.get(item_id)

        if status == "failed":
            failed_count += 1

            # A failed task must not have a refusal decision score.
            if result is not None and any(
                evaluation.name == "refusal_decision_correct"
                for evaluation in result.evaluations
            ):
                issues.append(
                    f"Failed task unexpectedly received a score: {item_id}"
                )

            continue

        if status != "completed":
            issues.append(
                f"Unresolved task: {item_id}, status={status}"
            )
            continue

        completed_count += 1
        answer_status = record.get("answer_status")

        if answer_status not in ("answered", "abstained"):
            issues.append(f"Invalid answer status: {item_id}")
            continue

        if answer_status == "abstained":
            abstained_count += 1
            reason = record.get("termination_reason") or "unknown"
            abstained_by_reason[reason] = (
                abstained_by_reason.get(reason, 0) + 1
            )

        if result is None:
            issues.append(f"Missing result: {item_id}")
            continue

        # Read the Gold label from the dataset item.
        expected_output = result.item.expected_output

        if (
            not isinstance(expected_output, dict)
            or type(expected_output.get("answerable")) is not bool
        ):
            issues.append(f"Gold label mismatch: {item_id}")
            continue
        answerable = expected_output["answerable"]

        scores = [
            evaluation.value
            for evaluation in result.evaluations
            if evaluation.name == "refusal_decision_correct"
        ]

        if (
            len(scores) != 1
            or type(scores[0]) not in (int, float)
            or scores[0] not in (0.0, 1.0)
        ):
            issues.append(
                f"Missing, duplicate or invalid refusal score: {item_id}"
            )
            continue

        expected_score = float(
            (answer_status == "answered") == answerable
        )

        if scores[0] != expected_score:
            issues.append(
                f"Score disagrees with execution record: {item_id}"
            )
            continue

        scored_count += 1
        correct_decision_count += int(scores[0])

        if answerable and answer_status == "abstained":
            false_refusal_count += 1

        if not answerable and answer_status == "answered":
            unanswerable_answered_count += 1

    planned_count = len(execution_records)
    assessment_complete = planned_count > 0 and not issues

    # Counts remain available even when assessment is incomplete.
    counts = {
        "planned_count": planned_count,
        "completed_count": completed_count,
        "execution_failed_count": failed_count,
        "scored_count": scored_count,
        "answerable_planned_count": answerable_planned_count,
        "unanswerable_planned_count": unanswerable_planned_count,
    }

    evaluations = [
        Evaluation(name=name, value=value)
        for name, value in counts.items()
    ]

    evaluations.extend(
        [
            Evaluation(
                name="abstained_count",
                value=abstained_count,
                comment=json.dumps(
                    {"termination_reason_counts": abstained_by_reason},
                    ensure_ascii=False,
                ),
            ),
            Evaluation(
                name="assessment_complete",
                value=float(assessment_complete),
                comment=json.dumps(
                    {
                        "issues": issues,
                        "note": (
                            "Complete means all planned items are accounted "
                            "for; classified execution failures may exist."
                        ),
                    },
                    ensure_ascii=False,
                ),
            ),
        ]
    )

    if not assessment_complete:
        return evaluations

    evaluations.append(
        Evaluation(
            name="execution_failure_rate",
            value=failed_count / planned_count,
            comment="Classified Agent execution failures / planned items.",
        )
    )

    metric_specs = (
        (
            "answerability_accuracy",
            correct_decision_count,
            planned_count,
            "Correct answer or refusal decisions / all planned items. "
            "Execution failures count as unsuccessful attempts."
            "Answer content correctness is not evaluated.",
        ),
        (
            "hallucination_rate",
            unanswerable_answered_count,
            unanswerable_planned_count,
            "Answered unanswerable items / all planned unanswerable items. "
            "Any list, including [], counts as an answer."
            "Execution failures are included only in the denominator.",
        ),
        (
            "false_refusal_rate",
            false_refusal_count,
            answerable_planned_count,
            "Abstained answerable items / all planned answerable items."
            "Execution failures are included only in the denominator.",
        ),
    )

    undefined_metrics = []

    for name, numerator, denominator, description in metric_specs:
        if denominator == 0:
            undefined_metrics.append(name)
            continue

        evaluations.append(
            Evaluation(
                name=name,
                value=numerator / denominator,
                comment=json.dumps(
                    {
                        "numerator": numerator,
                        "denominator": denominator,
                        "definition": description,
                    },
                    ensure_ascii=False,
                ),
            )
        )

    if undefined_metrics:
        # Keep undefined metrics absent rather than giving them a false zero.
        for evaluation in evaluations:
            if evaluation.name == "assessment_complete":
                details = json.loads(evaluation.comment)
                details["undefined_metrics_zero_denominator"] = (
                    undefined_metrics
                )
                evaluation.comment = json.dumps(
                    details, ensure_ascii=False
                )
                break

    return evaluations

def evaluate_graph_grounding(
    used_triples: list,
    gold_triples: list,
) -> dict:
    """Measure coverage of the full Gold supporting subgraph."""
    normalized_gold = normalize_triples(gold_triples)

    if not normalized_gold:
        raise ValueError("Gold supporting subgraph must not be empty.")

    normalized_used = normalize_triples(used_triples)
    matched_triples = normalized_used & normalized_gold

    return {
        "used_triple_count": len(normalized_used),
        "gold_triple_count": len(normalized_gold),
        "matched_triple_count": len(matched_triples),
        "graph_evidence_coverage": (
            len(matched_triples) / len(normalized_gold)
        ),
    }

def graph_grounding_evaluator(
    *,
    output,
    expected_output,
    **kwargs,
) -> Evaluation:
    """Score standard graph evidence coverage for one completed task."""
    if not isinstance(output, dict):
        raise ValueError("Task output must be a dictionary.")

    if output.get("execution_status") != "completed":
        raise ValueError(
            "Per-item graph evidence evaluation requires completed execution."
        )

    if (
        not isinstance(expected_output, dict)
        or "full_answer_subgraph_wikikg2" not in expected_output
    ):
        raise ValueError(
            "Expected output must contain 'full_answer_subgraph_wikikg2'."
        )

    if output.get("used_triples_error") is not None:
        raise ValueError(
            f"Evidence extraction failed: {output['used_triples_error']}"
        )

    if "used_triples" not in output or output["used_triples"] is None:
        raise ValueError("Task output has no available used_triples record.")

    evaluation = evaluate_graph_grounding(
        used_triples=output["used_triples"],
        gold_triples=expected_output["full_answer_subgraph_wikikg2"],
    )

    return Evaluation(
        name="graph_evidence_coverage",
        value=evaluation["graph_evidence_coverage"],
        comment=json.dumps(
            {
                "used_triple_count": evaluation["used_triple_count"],
                "gold_triple_count": evaluation["gold_triple_count"],
                "matched_triple_count": evaluation["matched_triple_count"],
            },
            ensure_ascii=False,
        ),
    )

def graph_grounding_summary_evaluator(
    *,
    item_results: list[ExperimentItemResult],
    execution_records: dict,
    **kwargs,
) -> list[Evaluation]:
    """Average evidence coverage over all planned items; failures contribute zero."""
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

    completed_count = 0
    failed_count = 0
    scored_count = 0
    coverage_sum = 0.0

    for item_id, record in execution_records.items():
        status = record["execution_status"]
        result = results_by_id.get(item_id)

        if status == "failed":
            failed_count += 1

            if result is not None:
                issues.append(
                    f"Failed task unexpectedly returned a result: {item_id}"
                )

            # Failure contributes zero, but remains in planned_count.
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
            if evaluation.name == "graph_evidence_coverage"
        ]

        if (
            len(scores) != 1
            or type(scores[0]) not in (int, float)
            or not math.isfinite(scores[0])
            or not 0.0 <= scores[0] <= 1.0
        ):
            issues.append(
                f"Missing, duplicate, or invalid graph evidence score: {item_id}"
            )
            continue

        scored_count += 1
        coverage_sum += scores[0]

    planned_count = len(execution_records)
    assessment_complete = planned_count > 0 and not issues

    evaluations = [
        Evaluation(name="GG_planned_count", value=planned_count),
        Evaluation(name="GG_completed_count", value=completed_count),
        Evaluation(name="GG_execution_failed_count", value=failed_count),
        Evaluation(name="GG_scored_count", value=scored_count),
        Evaluation(
            name="GG_assessment_complete",
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
                    name="mean_graph_evidence_coverage",
                    value=coverage_sum / planned_count,
                    comment=json.dumps(
                        {
                            "coverage_sum": coverage_sum,
                            "planned_count": planned_count,
                            "definition": (
                                "Sum of completed-item evidence coverage / "
                                "all planned items. Classified execution "
                                "failures contribute zero."
                            ),
                        },
                        ensure_ascii=False,
                    ),
                ),
                Evaluation(
                    name="GG_execution_failure_rate",
                    value=failed_count / planned_count,
                ),
            ]
        )

    return evaluations
