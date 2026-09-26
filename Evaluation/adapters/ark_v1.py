"""Adapt ARK v1 execution to the shared evaluation interface."""

from typing import Any

from langchain_core.runnables import RunnableConfig

class AgentExecutionError(RuntimeError):
    """An Agent execution or final-output failure."""

    def __init__(self, message: str, *, error_type: str):
        super().__init__(message)
        self.error_type = error_type

def run_ark_v1(
    *,
    sample: dict[str, Any],
    agent_config: dict[str, Any],
    runnable_config: RunnableConfig | None = None,
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
        final_state = agent.run(runnable_config=runnable_config)
    except Exception as error:
        raise AgentExecutionError(
            f"ARK v1 execution failed: "
            f"{type(error).__name__}: {error}",
            error_type="agent_execution_error",
        ) from error

    if final_state is None:
        raise AgentExecutionError(
            "ARK v1 finished without a final state.",
            error_type="missing_final_answer",
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

    return {
        "answer_payload": answer_payload,
        "execution_status": "completed",
        "answer_status": (
            "abstained" if answer_payload is None else "answered"
        ),
    }