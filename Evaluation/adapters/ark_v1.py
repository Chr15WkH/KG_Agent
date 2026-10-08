"""Adapt ARK v1 execution to the shared evaluation interface."""

from typing import Any

from langchain_core.runnables import RunnableConfig

class AgentExecutionError(RuntimeError):
    """An Agent execution or final-output failure."""

    def __init__(self, message: str, *, error_type: str):
        super().__init__(message)
        self.error_type = error_type

def _extract_used_triples(final_state: dict[str, Any]) -> list[list[str]]:
    """Extract selected triples from retained, completed, valid steps."""
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

        reasoning_result = result.get("result")
        if not isinstance(reasoning_result, dict):
            raise ValueError(f"Reasoning step {index} has no reasoning result.")

        reset = reasoning_result.get("reset_reasoning_step")
        if type(reset) is not bool:
            raise ValueError(f"Reasoning step {index} has invalid reset status.")

        if reset:
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

def run_ark_v1(
    *,
    sample: dict[str, Any],
    agent_config: dict[str, Any],
    runnable_config: RunnableConfig | None = None,
    verbose: bool = True,
) -> dict[str, Any]:
    """Run ARK v1 on one raw GTSQA sample and return its answer."""

    # Import only when this adapter is called.
    # The experiment entry point must load the environment first.
    from ark_v1.ark_v1 import ARK_V1
    from ark_v1.adapters.gtsqa import adapt_gtsqa_sample
    from ark_v1.data_models.agent_models import QuestionTypes

    adapted_sample = adapt_gtsqa_sample(sample)

    agent = ARK_V1()
    agent.load_configuration(config=agent_config)
    agent.load_graph_data(adapted_sample["graph"])
    agent.set_initial_state(
        question=adapted_sample["question"],
        question_type=QuestionTypes.ENTITY_LIST,
    )

    try:
        final_state = agent.run(runnable_config=runnable_config, verbose=verbose)
    except Exception as error:
        raise AgentExecutionError(
            f"ARK v1 execution failed: "
            f"{type(error).__name__}: {error}",
            error_type="agent_execution_error",
        ) from error

    if final_state is None:
        raise AgentExecutionError(
            "ARK v1 finished without a final state.",
            error_type="missing_final_state",
        )

    if not isinstance(final_state, dict):
        raise AgentExecutionError(
            "ARK v1 returned a non-dictionary final state.",
            error_type="invalid_final_answer",
        )

    final_answer = final_state.get("finalAnswer")

    if final_answer is None:
        raise AgentExecutionError(
            "ARK v1 finished without a final answer.",
            error_type="missing_final_answer",
        )

    if (
        not isinstance(final_answer, dict)
        or "answer" not in final_answer
    ):
        raise AgentExecutionError(
            "ARK v1 final answer must be a dictionary "
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

    return {
        "answer_payload": answer_payload,
        "execution_status": "completed",
        "answer_status": (
            "abstained" if answer_payload is None else "answered"
        ),
        "termination_reason": final_state.get("termination_reason"),
        "used_triples": used_triples,
        "used_triples_error": used_triples_error,
    }