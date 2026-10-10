"""Run a Langfuse dataset experiment with a selected Agent."""

import os
import logging
from pathlib import Path
from functools import partial
from dotenv import load_dotenv

from Evaluation.evaluators import (
    entity_exact_match_evaluator,
    entity_exact_match_summary_evaluator,
    refusal_evaluator,
    refusal_summary_evaluator,
    graph_grounding_evaluator,
    graph_grounding_summary_evaluator,
    boolean_exact_match_evaluator,
)
from Evaluation.dataset_loader import load_gtsqa_sample
from Evaluation.prepare_dataset import prepare_dataset
from Evaluation.langfuse_support import (
    initialize_langfuse,
    create_langfuse_callback,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Experiment configuration
AGENT_VERSION = "ark_v1_1"
# Choose the dataset
DATASET_TYPE = "crlt" # “gtsqa”, "gtsqa_ua" or "crlt"
DATASET_NAME = "CR-LT-KGQA" #"gtsqa-development", "gtsqa-ua-development" or "CR-LT-KGQA"
# Select exactly which samples to run, in this order.
# Sample IDs for GTSQA:
# SAMPLE_IDS = (
#     13311,
#     37715,
#     40154,
#     42587,
#     4519,
#     8865,
#     16154,
#     31606,
#     33122,
#     40487,
#     1012,
#     41371,
# )
# Sample IDs for GTSQA_UA:
# SAMPLE_IDS = (
#     "13311-original",
#     "13311-ua-01",
#     "37715-original",
#     "37715-ua-01",
#     "40154-original",
#     "40154-ua-01",
#     "42587-original",
#     "42587-ua-01",
#     "4519-original",
#     "4519-ua-01",
#     "8865-original",
#     "8865-ua-01",
#     "16154-original",
#     "16154-ua-01",
#     "31606-original",
#     "31606-ua-01",
#     "33122-original",
#     "33122-ua-01",
#     "40487-original",
#     "40487-ua-01",
#     "1012-original",
#     "1012-ua-01",
#     "41371-original",
    # "41371-ua-01",
# )
# Sample IDs for CR-LT-KGQA:
SAMPLE_IDS = (
    "S2",
    "S3",
    "S101",
    "S104",
    "S107",
    "S115",
    "S123",
    "S176",
    "S183",
    "S185",
    "S188",
    "S192",
    "S195",
    "S198",
    "S200",
)
# Allow creation of missing datasets and items.
SYNC_MISSING_ITEMS = False
# Update existing items when local content changes.
UPDATE_EXISTING_ITEMS = False
EXPERIMENT_NAME = "ark-v1-qwen3.8-27b-crlt-bool-em-15items-01"
ENV_FILE = PROJECT_ROOT / ".env"

# Print detailed Agent messages when debugging.
AGENT_VERBOSE = False

AGENT_CONFIG = {
    "complete_answer_qids": DATASET_TYPE == "gtsqa",
    "llm": {
        # "model": "deepseek/deepseek-chat", # "deepseek/deepseek-chat" for openrouter, "qwen3.5:9b" and "qwen3.8:2.7b" for litellm
        "model": "qwen3.8:27b", # "deepseek/deepseek-chat" for openrouter, "qwen3.5:9b" and "qwen3.8:2.7b" for litellm
        "temperature": 0.9,
        "top_p": 0.9,
        "seed": 42,
    },
}


def main() -> None:
    # Select item and run evaluators for the dataset.
    if DATASET_TYPE == "gtsqa":
        item_evaluators = [entity_exact_match_evaluator, graph_grounding_evaluator,]
        summary_evaluators = [entity_exact_match_summary_evaluator, graph_grounding_summary_evaluator,]
        evaluation_description = "entity exact-match and graph evidence coverage evaluation"

    elif DATASET_TYPE == "gtsqa_ua":
        item_evaluators = [refusal_evaluator,]
        summary_evaluators = [refusal_summary_evaluator,]
        evaluation_description = "answer/refusal decision evaluation"

    elif DATASET_TYPE == "crlt":
        item_evaluators = [boolean_exact_match_evaluator]
        summary_evaluators = [
            partial(
                entity_exact_match_summary_evaluator,
                score_name="boolean_exact_match",
            )
        ]
        evaluation_description = "Boolean exact-match and end-to-end accuracy evaluation"

    else:
        raise ValueError(f"Unsupported dataset type: {DATASET_TYPE}")

    if not ENV_FILE.is_file():
        raise FileNotFoundError(
            f"Environment file not found: {ENV_FILE}"
        )

    load_dotenv(ENV_FILE, override=True)

    log_level = (
        logging.INFO if AGENT_VERBOSE else logging.WARNING
    )

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    # Set before the adapter lazily imports Agent/LiteLLM.
    os.environ["LITELLM_LOG"] = (
        "INFO" if AGENT_VERBOSE else "WARNING"
    )

    # Load only the selected Agent adapter.
    if AGENT_VERSION == "ark_v1_1":
        from Evaluation.adapters.ark_v1_1 import run_ark_v1_1, AgentExecutionError

        run_agent = run_ark_v1_1
    else:
        raise ValueError(f"Unsupported Agent: {AGENT_VERSION}")

    client = initialize_langfuse()

    try:
        selected_items = prepare_dataset(
            client=client,
            dataset_name=DATASET_NAME,
            sample_ids=SAMPLE_IDS,
            dataset_type=DATASET_TYPE,
            sync_missing_items=SYNC_MISSING_ITEMS,
            update_existing_items=UPDATE_EXISTING_ITEMS,
        )
        
        # Keep CRLT graphs for the Agent, outside experiment metadata.
        crlt_graphs = {}

        if DATASET_TYPE == "crlt":
            crlt_graphs = {
                item.id: item.metadata["graph"]
                for item in selected_items
            }

            selected_items = [
                item.model_copy(
                    update={
                        "metadata": {
                            "sample_id": item.id,
                            "dataset_type": "crlt",
                        }
                    }
                )
                for item in selected_items
            ]
        # Count answerable and unanswerable items for GTSQA_UA.
        if DATASET_TYPE == "gtsqa_ua":
            # Number of planned answerable items
            answerable_planned_count = sum(
                item.expected_output["answerable"]
                for item in selected_items
            )
            # Number of planned unanswerable items
            unanswerable_planned_count = (
                len(selected_items) - answerable_planned_count
            )

        # Pre-register all items so failed tasks remain visible in experiment statistics.
        execution_records = {
            item.id: {
                "sample_id": (
                    item.id
                    if DATASET_TYPE == "crlt"
                    else str((item.metadata or {}).get("sample_id", ""))
                ),
                "execution_status": "not_started",
                "answer_status": None,
                "termination_reason": None,
                "error_type": None,
                "error_message": None,
            }
            for item in selected_items
        }

        item_positions = {
            item.id: position
            for position, item in enumerate(selected_items, start=1)
        }
        total_items = len(execution_records)

        def task(*, item, **kwargs):
            record = execution_records[item.id]
            record["execution_status"] = "running"

            # Show the item's position and sample ID in progress messages.
            progress_label = (
                f"[{item_positions[item.id]}/{total_items}] "
                f"sample={record['sample_id']}"
            )
            print(f"{progress_label} Started", flush=True)

            try:
                if DATASET_TYPE == "crlt":
                    sample_id = item.id
                    sample = {
                        "id": sample_id,
                        "question": item.input,
                        "graph": crlt_graphs[item.id],
                    }
                elif DATASET_TYPE == "gtsqa":
                    sample_id = int(item.metadata["sample_id"])
                    sample = load_gtsqa_sample(sample_id)
                else:
                    from ark_v1_1.adapters.gtsqa_ua import (
                        load_gtsqa_ua_sample,
                    )

                    sample_id = str(item.metadata["sample_id"])
                    sample = load_gtsqa_ua_sample(sample_id)

                if sample["question"] != item.input:
                    raise ValueError(
                        f"Question mismatch for sample {sample_id}."
                    )

                # Created inside the experiment task so the callback
                # can join the task's active trace
                callback = create_langfuse_callback()

                output = run_agent(
                    sample=sample,
                    dataset_type=DATASET_TYPE,
                    agent_config=AGENT_CONFIG,
                    verbose=AGENT_VERBOSE,
                    runnable_config={
                        "callbacks": [callback],
                        "run_name": AGENT_VERSION,
                        "metadata": {
                            "sample_id": str(sample_id),
                            "agent_version": AGENT_VERSION,
                        },
                    },
                )

            except AgentExecutionError as error:
                record.update(
                    execution_status="failed",
                    answer_status=None,
                    error_type=error.error_type,
                    error_message=str(error),
                )
                print(f"{progress_label} Execution failed | {error.error_type}", flush=True,)
                raise

            except Exception as error:
                record.update(
                    execution_status="task_error",
                    answer_status=None,
                    error_type=type(error).__name__,
                    error_message=str(error),
                )
                print(
                    f"{progress_label} Task error | {type(error).__name__}", flush=True)
                raise

            record.update(
                execution_status=output["execution_status"],
                answer_status=output["answer_status"],
                termination_reason=output.get("termination_reason"),
            )

            reason_text = ""
            if output["answer_status"] == "abstained":
                reason = output.get("termination_reason") or "unknown"
                reason_text = f" | reason={reason}"

            print(
                f"{progress_label} Execution completed | {output['answer_status']}{reason_text} | Evaluation pending", flush=True)

            return output

        # Pass execution records and required counts to run evaluators.
        summary_kwargs = {
            "execution_records": execution_records,
        }

        if DATASET_TYPE == "gtsqa_ua":
            summary_kwargs.update(
                answerable_planned_count=answerable_planned_count,
                unanswerable_planned_count=unanswerable_planned_count,
            )

        run_evaluators = [
            partial(evaluator, **summary_kwargs)
            for evaluator in summary_evaluators
        ]
        
        result = client.run_experiment(
            name=EXPERIMENT_NAME,
            description=(
                f"{DATASET_TYPE} development experiment with "
                f"{len(selected_items)} selected items "
                f"and {evaluation_description}."
            ),
            data=selected_items,
            task=task,
            evaluators=item_evaluators,
            run_evaluators=run_evaluators,
            max_concurrency=1,
            metadata={
                "agent_version": AGENT_VERSION,
                "agent_config": AGENT_CONFIG,
                "dataset_type": DATASET_TYPE,
                "dataset": DATASET_NAME,
                "sample_count": len(selected_items),
            },
        )

        print(result.format())
        print("Dataset run ID:", result.dataset_run_id)
        print("Dataset run URL:", result.dataset_run_url)

    finally:
        client.shutdown()


if __name__ == "__main__":
    main()
