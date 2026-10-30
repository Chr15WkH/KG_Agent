"""Adapt ARK v2 execution to the shared evaluation interface."""

from typing import Any

from langchain_core.runnables import RunnableConfig

class AgentExecutionError(RuntimeError):
    """An Agent execution or final-output failure."""

    def __init__(self, message: str, *, error_type: str):
        super().__init__(message)
        self.error_type = error_type

def _extract_used_triples(final_state: dict[str, Any]) -> list[list[str]]:
    """
    Extract the Used Triples of finished, valid and not discarded steps.
    These are the same steps whose triples appear in the exploration summary
    and are used to complete answer QIDs.
    """
    steps = final_state.get("reasoningSteps")

    if not isinstance(steps, list):
        raise ValueError("Final state must contain a reasoningSteps list.")

    used_triples = []

    for index, step in enumerate(steps):
        if not isinstance(step, dict):
            raise ValueError(f"Reasoning step {index} must be a dictionary.")

        finished = step.get("finished")
        if type(finished) is not bool:
            raise ValueError(f"Reasoning step {index} has invalid finished status.")

        if not finished:
            continue

        result = step.get("result")
        if not isinstance(result, dict):
            raise ValueError(f"Completed step {index} has no valid result.")

        valid = result.get("valid")
        if type(valid) is not bool:
            raise ValueError(f"Reasoning step {index} has invalid verification status.")

        if not valid:
            continue

        discarded = step.get("discarded")
        if type(discarded) is not bool:
            raise ValueError(f"Reasoning step {index} has invalid discarded status.")

        if discarded:
            continue

        triples = result.get("triples")
        if not isinstance(triples, list):
            raise ValueError(f"Reasoning step {index} has no selected triples list.")

        for triple in triples:
            try:
                head = triple["head"]["value"]
                relation = triple["edge"]["value"]["relation"]
                tail = triple["tail"]["value"]
            except (KeyError, TypeError) as error:
                raise ValueError(
                    f"Invalid selected triple structure in step {index}."
                ) from error

            if not all(
                isinstance(value, str) and value.strip()
                for value in (head, relation, tail)
            ):
                raise ValueError(
                    f"Selected triple fields in step {index} "
                    "must be non-empty strings."
                )

            used_triples.append([head, relation, tail])

    return used_triples

# Exploration Trace

def _format_triple(triple: dict[str, Any]) -> str:
    """Format a dumped triple as "head, relation, tail", as in the exploration summary."""
    relation = triple["edge"]["value"].get("relation", "")
    return f"{triple['head']['value']}, {relation}, {triple['tail']['value']}"

def _trace_steps(steps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Describe each reasoning step for the trace.
    Status is one of:
    - "incomplete": the step ended before a reasoning result was checked
      (anchor, relation or reasoning attempt limit);
    - "invalid": the last reasoning attempt used invalid keys;
    - "discarded": valid, but the triples were irrelevant;
    - "valid": valid and kept.
    Used Triples, action and next_anchor are only shown for valid or
    discarded steps, because an invalid step may keep an earlier attempt's result.
    """
    rows = []
    for iteration, step in enumerate(steps, start=1):
        anchor = step.get("anchor") or {}
        relation = step.get("relation_selected") or {}
        result = step.get("result") or {}

        if not step.get("finished"):
            status = "incomplete"
        elif not result.get("valid"):
            status = "invalid"
        elif step.get("discarded"):
            status = "discarded"
        else:
            status = "valid"

        row = {
            "iteration": iteration,
            "anchor": anchor["anchor"]["value"] if anchor.get("valid") else None,
            "relation": (
                f"{relation['candidate']['value']} ({relation['candidate']['direction']})"
                if relation.get("valid")
                else None
            ),
            "status": status,
            "reasoning_attempts": result.get("attempt", 0),
        }
        if status in ("valid", "discarded"):
            reasoning = result["result"]
            row["used_triples"] = [_format_triple(t) for t in result["triples"]]
            row["action"] = reasoning["action"]
            row["next_anchor"] = reasoning["next_anchor"]
        rows.append(row)
    return rows

def _build_exploration_trace(final_state: dict[str, Any]) -> dict[str, Any]:
    """Collect the reasoning steps and the exploration record for the trace.

    The record is shown in full (also rejected and overwritten conclusions),
    unlike the exploration summary, which shows only the latest lines.
    Triples are shortened to "head, relation, tail".
    """
    exploration = final_state["exploration"]

    conclusions = []
    for record in exploration["conclusions"]:
        conclusions.append(
            {
                "conclusion_id": record["conclusion_id"],
                "iteration": record["iteration"],
                "candidate": record["candidate"],
                "condition": record["condition"],
                "status": record["status"],
                "evidence_type": record["evidence_type"],
                "triples": [_format_triple(t) for t in record["triples"]],
                "absent_entity": record["absent_entity"],
                "query": record["query"],
                "verified": record["verified"],
                "rejection_reason": record["rejection_reason"],
            }
        )

    candidates = [
        {
            "name": candidate["name"],
            "source_iteration": candidate["source_iteration"],
            "status": candidate["status"],
            "conclusion_ids": candidate["conclusion_ids"],
        }
        for candidate in exploration["candidates"]
    ]

    return {
        "steps": _trace_steps(final_state["reasoningSteps"]),
        "conclusions": conclusions,
        "candidates": candidates,
    }

def run_ark_v2(
    *,
    sample: dict[str, Any],
    dataset_type: str = "gtsqa",
    agent_config: dict[str, Any],
    runnable_config: RunnableConfig | None = None,
    verbose: bool = True,
) -> dict[str, Any]:
    """Run ARK v2 on one raw sample and return its answer and exploration trace."""

    # Import only when this adapter is called.
    # The experiment entry point must load the environment first.
    from ark_v2.ark_v2 import ARK_V2
    from ark_v2.adapters.gtsqa import adapt_gtsqa_sample
    from ark_v2.data_models.agent_models import QuestionTypes

    if dataset_type == "crlt":
        adapted_sample = sample
        question_type = QuestionTypes.YES_NO
    elif dataset_type in ("gtsqa", "gtsqa_ua"):
        adapted_sample = adapt_gtsqa_sample(sample)
        question_type = QuestionTypes.ENTITY_LIST
    else:
        raise ValueError(f"Unsupported dataset type: {dataset_type}")

    agent = ARK_V2()
    agent.load_configuration(config=agent_config)
    agent.load_graph_data(adapted_sample["graph"])
    agent.set_initial_state(
        question=adapted_sample["question"],
        question_type=question_type,
    )

    try:
        final_state = agent.run(runnable_config=runnable_config, verbose=verbose)
    except Exception as error:
        raise AgentExecutionError(
            f"ARK v2 execution failed: "
            f"{type(error).__name__}: {error}",
            error_type="agent_execution_error",
        ) from error

    if final_state is None:
        raise AgentExecutionError(
            "ARK v2 finished without a final state.",
            error_type="missing_final_state",
        )

    if not isinstance(final_state, dict):
        raise AgentExecutionError(
            "ARK v2 returned a non-dictionary final state.",
            error_type="invalid_final_answer",
        )

    final_answer = final_state.get("finalAnswer")

    if final_answer is None:
        raise AgentExecutionError(
            "ARK v2 finished without a final answer.",
            error_type="missing_final_answer",
        )

    if (
        not isinstance(final_answer, dict)
        or "answer" not in final_answer
    ):
        raise AgentExecutionError(
            "ARK v2 final answer must be a dictionary "
            "containing the 'answer' field.",
            error_type="invalid_final_answer",
        )

    answer_payload = final_answer["answer"]

    try:
        used_triples = _extract_used_triples(final_state)
        used_triples_error = None
    except ValueError as error:
        # Evidence extraction failure must not invalidate Agent execution or EM.
        # Only Graph Grounding should be unavailable.
        used_triples = None
        used_triples_error = str(error)

    try:
        exploration = _build_exploration_trace(final_state)
        exploration_error = None
    except (KeyError, TypeError, AttributeError) as error:
        # The trace is only for inspection; a failure must not affect evaluation.
        exploration = None
        exploration_error = f"{type(error).__name__}: {error}"

    return {
        "answer_payload": answer_payload,
        "execution_status": "completed",
        "answer_status": (
            "abstained" if answer_payload is None else "answered"
        ),
        "termination_reason": final_state.get("termination_reason"),
        "used_triples": used_triples,
        "used_triples_error": used_triples_error,
        "exploration": exploration,
        "exploration_error": exploration_error,
    }
