"""Run a Langfuse dataset experiment with a selected Agent."""

import logging
from pathlib import Path

from dotenv import load_dotenv

from Evaluation.evaluators import entity_exact_match_evaluator
from Evaluation.gtsqa_data import load_sample, load_gold
from Evaluation.langfuse_support import (
    initialize_langfuse,
    create_langfuse_callback,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Experiment configuration
AGENT_VERSION = "ark_v1"
DATASET_NAME = "gtsqa-development"
EXPERIMENT_NAME = "ark-v1-deepseek-pilot"
ENV_FILE = PROJECT_ROOT / "agent" / "ark_v1" / ".env"

AGENT_CONFIG = {
    "llm": {
        "model": "deepseek/deepseek-chat",
        "temperature": 0.9,
        "top_p": 0.9,
        "seed": 42,
    },
}


def main() -> None:
    if not ENV_FILE.is_file():
        raise FileNotFoundError(
            f"Environment file not found: {ENV_FILE}"
        )

    load_dotenv(ENV_FILE, override=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    if AGENT_VERSION == "ark_v1":
        from Evaluation.adapters.ark_v1 import run_ark_v1

        run_agent = run_ark_v1
    else:
        raise ValueError(f"Unsupported Agent: {AGENT_VERSION}")

    client = initialize_langfuse()

    try:
        dataset = client.get_dataset(DATASET_NAME)

        # Keep the first experiment limited to the prepared pilot item.
        if (
            len(dataset.items) != 1
            or dataset.items[0].status != "ACTIVE"
            or str(
                (dataset.items[0].metadata or {}).get("sample_id")
            ) != "13311"
        ):
            raise ValueError(
                "This pilot expects exactly one active item: 13311."
            )

        # Check the hosted reference before any model calls.
        item = dataset.items[0]
        gold = load_gold(13311)

        if (
            item.input != gold["question"]
            or item.expected_output != gold["gold_answer"]
        ):
            raise ValueError(
                "Langfuse dataset item differs from local Gold."
            )

        def task(*, item, **kwargs):
            sample_id = int(item.metadata["sample_id"])
            sample = load_sample(sample_id)

            if sample["question"] != item.input:
                raise ValueError(
                    f"Question mismatch for sample {sample_id}."
                )

            # Created inside the experiment task so the callback
            # can join the task's active trace.
            callback = create_langfuse_callback()

            return run_agent(
                sample=sample,
                agent_config=AGENT_CONFIG,
                runnable_config={
                    "callbacks": [callback],
                    "run_name": AGENT_VERSION,
                    "metadata": {
                        "sample_id": str(sample_id),
                        "agent_version": AGENT_VERSION,
                    },
                },
            )

        result = dataset.run_experiment(
            name=EXPERIMENT_NAME,
            description=(
                "Single-item GTSQA development experiment "
                "with entity exact-match evaluation."
            ),
            task=task,
            evaluators=[entity_exact_match_evaluator],
            max_concurrency=1,
            metadata={
                "agent_version": AGENT_VERSION,
                "agent_config": AGENT_CONFIG,
                "dataset": DATASET_NAME,
            },
        )

        print(result.format())
        print("Dataset run ID:", result.dataset_run_id)
        print("Dataset run URL:", result.dataset_run_url)

    finally:
        client.shutdown()


if __name__ == "__main__":
    main()