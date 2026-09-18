"""Adapt ARK v1 execution to the shared evaluation interface."""

from typing import Any

from langchain_core.runnables import RunnableConfig


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

    final_state = agent.run(runnable_config=runnable_config)

    if (
        final_state is None
        or final_state.get("finalAnswer") is None
    ):
        raise RuntimeError(
            "ARK v1 finished without a final answer."
        )

    final_answer = final_state["finalAnswer"]

    if "answer" not in final_answer:
        raise RuntimeError(
            "ARK v1 final answer is missing the 'answer' field."
        )

    return {
        "answer_payload": final_answer["answer"],
    }