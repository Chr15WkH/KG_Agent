"""Run a Langfuse dataset experiment with a selected Agent."""

import os
import logging
import sys
import json
from datetime import datetime
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
from Evaluation.dataset_loader import gtsqa_ua_paths, load_gtsqa_sample
from Evaluation.prepare_dataset import prepare_dataset
from Evaluation.splits import resolve_selection
from Evaluation.langfuse_support import (
    initialize_langfuse,
    create_langfuse_callback,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


# ======================================================================
# Experiment configuration
# ======================================================================

# Choose the Agent
AGENT_VERSION = "ark_v2" # "ark_v1" (CRLT only), "ark_v1_1", "ark_v2"

# Choose the dataset
DATASET_TYPE = "gtsqa" # "gtsqa", "gtsqa_ua" or "crlt"

# Choose the split. Sample IDs and the Langfuse dataset name come from
# Dataset/splits/<dataset>_splits.json, so development and test never mix.
SPLIT = "development" # "development" or "test"

# None runs the whole split in manifest order.
# A tuple runs only these samples, in this order; every ID must belong to SPLIT.
# GTSQA IDs are integers (e.g. 13311), GTSQA_UA IDs are strings
# (e.g. "13311-original", "13311-ua-01"), CRLT IDs are strings (e.g. "S2").
SAMPLE_IDS = None

# Allow creation of missing datasets and items.
SYNC_MISSING_ITEMS = True

# Update existing items when local content changes.
UPDATE_EXISTING_ITEMS = False
ENV_FILE = PROJECT_ROOT / ".env"
# Terminal output (.log) and a compact record of each run (.json) are saved here.
RESULTS_DIR = PROJECT_ROOT / "results" / "experiments"

# Print detailed Agent messages when debugging.
AGENT_VERBOSE = False

AGENT_CONFIG = {
    "complete_answer_qids": DATASET_TYPE == "gtsqa",
    # ARK v2 only: show known entities and their common neighbours in Step 2.1.
    # Written explicitly so the setting is recorded in the experiment metadata.
    "known_entities_hint": True,
    # ARK v2 only: split the request into constraints and show them with their status in the summary.
    "request_decomposition": False,
    # ARK v2 only: output token limit of the reasoning node (other nodes keep the LLM default).
    "reasoning_max_tokens": 3000,
    "llm": {
        # "model": "deepseek/deepseek-chat", # "deepseek/deepseek-chat" for openrouter, "qwen3.5:9b" and "qwen3.8:2.7b" for litellm
        "model": "qwen3.8:27b", # "deepseek/deepseek-chat" and "qwen/qwen3.8-27b" for openrouter, "qwen3.5:9b" and "qwen3.8:27b" for litellm
        "temperature": 0.9,
        "top_p": 0.9,
        "seed": 42,
    },
}


class _Tee:
    """Send everything written to a terminal stream also to a log file."""

    def __init__(self, stream, log_file):
        self.stream = stream
        self.log_file = log_file

    def write(self, text):
        self.stream.write(text)
        self.log_file.write(text)
        return len(text)

    def flush(self):
        self.stream.flush()
        self.log_file.flush()

    def __getattr__(self, name):
        # isatty, fileno, encoding, ... come from the terminal stream
        return getattr(self.stream, name)


def _write_run_record(path, *, result, execution_records, experiment_name, started_at):
    """
    Save a compact record of one run: run identifiers, agent configuration, run-level scores,
    and one entry per planned item. Failed items are not in result.item_results,
    so they appear with their execution record only (no answer, no scores).
    """
    item_results = {
        getattr(item_result.item, "id", None): item_result
        for item_result in result.item_results
    }

    items = []
    for item_id, record in execution_records.items():
        item_result = item_results.get(item_id)
        output = item_result.output if item_result and isinstance(item_result.output, dict) else {}
        # Only ARK v2 returns an exploration trace with steps
        steps = (output.get("exploration") or {}).get("steps")
        items.append(
            {
                **record,
                "answer": output.get("answer_payload"),
                "steps": len(steps) if steps is not None else None,
                "scores": (
                    {evaluation.name: evaluation.value for evaluation in item_result.evaluations}
                    if item_result
                    else {}
                ),
            }
        )

    data = {
        "run": {
            "experiment_name": experiment_name,
            "run_name": result.run_name,
            "dataset_run_id": result.dataset_run_id,
            "dataset_run_url": result.dataset_run_url,
            "started_at": f"{started_at:%Y-%m-%d %H:%M:%S}",
            "agent_version": AGENT_VERSION,
            "dataset_type": DATASET_TYPE,
            "split": SPLIT,
            "agent_config": AGENT_CONFIG,
        },
        "summary": {evaluation.name: evaluation.value for evaluation in result.run_evaluations},
        "items": items,
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def main() -> None:
    # Resolve the sample selection first, before any remote call.
    selection = resolve_selection(DATASET_TYPE, SPLIT, SAMPLE_IDS)
    dataset_name = selection["dataset_name"]
    sample_ids = selection["sample_ids"]
    selection_mode = selection["selection_mode"]

    # Select item and run evaluators for the dataset.
    if DATASET_TYPE == "gtsqa":
        item_evaluators = [entity_exact_match_evaluator, graph_grounding_evaluator,]
        summary_evaluators = [entity_exact_match_summary_evaluator, graph_grounding_summary_evaluator,]
        evaluation_description = "entity exact-match and graph evidence coverage evaluation"
        evaluator_label = "entity_em+grounding"

    elif DATASET_TYPE == "gtsqa_ua":
        item_evaluators = [refusal_evaluator,]
        summary_evaluators = [refusal_summary_evaluator,]
        evaluation_description = "answer/refusal decision evaluation"
        evaluator_label = "refusal"

    elif DATASET_TYPE == "crlt":
        item_evaluators = [boolean_exact_match_evaluator]
        summary_evaluators = [
            partial(
                entity_exact_match_summary_evaluator,
                score_name="boolean_exact_match",
            )
        ]
        evaluation_description = "Boolean exact-match and end-to-end accuracy evaluation"
        evaluator_label = "bool_em"

    else:
        raise ValueError(f"Unsupported dataset type: {DATASET_TYPE}")
    # Define the Experiment name: agent-model-dataset-split[-manual]-evaluator-item count.
    split_label = SPLIT if selection_mode == "full_split" else f"{SPLIT}-manual"
    # ARK v2 runs carry the switch settings, e.g. h1d0 = known entities hint on, request decomposition off.
    config_label = ""
    if AGENT_VERSION == "ark_v2":
        config_label = (
            f"-h{int(AGENT_CONFIG.get('known_entities_hint', False))}"
            f"d{int(AGENT_CONFIG.get('request_decomposition', False))}"
        )
    experiment_name = f"{AGENT_VERSION}{config_label}-{AGENT_CONFIG['llm']['model']}-{DATASET_TYPE}-{split_label}-{evaluator_label}-{len(sample_ids)}items"

    # From here on, everything printed in the terminal also goes to results/experiments/<start time>_<name>.log.
    # The log is line buffered, so it is complete up to the last line even if the run stops early;
    # the streams are not restored because the process ends with main().
    started_at = datetime.now()
    file_stem = f"{started_at:%Y%m%d-%H%M%S}_{experiment_name.replace(':', '_')}"
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    log_file = open(RESULTS_DIR / f"{file_stem}.log", "w", encoding="utf-8", buffering=1)
    sys.stdout = _Tee(sys.stdout, log_file)
    sys.stderr = _Tee(sys.stderr, log_file)

    print(f"Experiment: {experiment_name}", flush=True)
    print(
        f"Selection: {DATASET_TYPE} | split={SPLIT} | mode={selection_mode} | "
        f"items={len(sample_ids)} | Langfuse dataset={dataset_name}",
        flush=True,
    )

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
    if AGENT_VERSION == "ark_v1":
        # ARK v1 is only evaluated on CRLT; stop before a Langfuse run is created.
        if DATASET_TYPE != "crlt":
            raise ValueError(
                f"ARK v1 supports only the CRLT dataset, got: {DATASET_TYPE}"
            )

        from Evaluation.adapters.ark_v1 import run_ark_v1, AgentExecutionError

        run_agent = run_ark_v1

    elif AGENT_VERSION == "ark_v1_1":
        from Evaluation.adapters.ark_v1_1 import run_ark_v1_1, AgentExecutionError

        run_agent = run_ark_v1_1

    elif AGENT_VERSION == "ark_v2":
        from Evaluation.adapters.ark_v2 import run_ark_v2, AgentExecutionError

        run_agent = run_ark_v2

    else:
        raise ValueError(f"Unsupported Agent: {AGENT_VERSION}")

    client = initialize_langfuse()

    try:
        selected_items = prepare_dataset(
            client=client,
            dataset_name=dataset_name,
            sample_ids=sample_ids,
            dataset_type=DATASET_TYPE,
            split=SPLIT,
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
                    sample = load_gtsqa_sample(sample_id, split=SPLIT)
                else:
                    # ARK v1.1 and ARK v2 share this GTSQA_UA loader, so both Agents receive the same samples.
                    from ark_v1_1.adapters.gtsqa_ua import (
                        load_gtsqa_ua_sample,
                    )

                    sample_id = str(item.metadata["sample_id"])
                    ua_gold_path, ua_input_path = gtsqa_ua_paths(SPLIT)
                    sample = load_gtsqa_ua_sample(
                        sample_id,
                        gold_path=ua_gold_path,
                        input_path=ua_input_path,
                    )

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
            name=experiment_name,
            description=(
                f"{DATASET_TYPE} {SPLIT} experiment ({selection_mode}) with "
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
                "dataset": dataset_name,
                "split": SPLIT,
                "selection_mode": selection_mode,
                "sample_count": len(selected_items),
            },
        )

        print(result.format())
        print("Dataset run ID:", result.dataset_run_id)
        print("Dataset run URL:", result.dataset_run_url)

        record_path = RESULTS_DIR / f"{file_stem}.json"
        _write_run_record(
            record_path,
            result=result,
            execution_records=execution_records,
            experiment_name=experiment_name,
            started_at=started_at,
        )
        print("Run record:", record_path)

    finally:
        client.shutdown()


if __name__ == "__main__":
    main()
