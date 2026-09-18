"""Run one development sample with Langfuse tracing."""

import json
import logging
from pathlib import Path

from dotenv import load_dotenv

from Evaluation.langfuse_support import (
    initialize_langfuse,
    create_langfuse_callback,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Experiment configuration
AGENT_VERSION = "ark_v1"
SAMPLE_ID = 40154
ENV_FILE = PROJECT_ROOT / "agent" / "ark_v1" / ".env"

AGENT_CONFIG = {
    "llm": {
        "model": "deepseek/deepseek-chat", # "deepseek/deepseek-chat" for openrouter, "qwen3.5:9b" and "qwen3.8:2.7b" for litellm
        "temperature": 0.9,
        "top_p": 0.9,
        "seed": 42,
    },
}

def load_sample(sample_id: int) -> dict:
    """Load one raw GTSQA sample without converting its graph."""
    input_path = PROJECT_ROOT / "Dataset" / "gtsqa_development_agent_input.jsonl"

    with input_path.open("r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue

            sample = json.loads(line)

            if str(sample["id"]) == str(sample_id):
                return sample

    raise ValueError(f"GTSQA sample {sample_id} was not found.")


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

    # Load only the selected Agent adapter.
    if AGENT_VERSION == "ark_v1":
        from Evaluation.adapters.ark_v1 import run_ark_v1

        run_agent = run_ark_v1
    else:
        raise ValueError(f"Unsupported Agent: {AGENT_VERSION}")

    sample = load_sample(SAMPLE_ID)

    # Keep the settings of the existing LiteLLM example.
    agent_config = AGENT_CONFIG

    metadata = {
        "sample_id": str(SAMPLE_ID),
        "dataset": "gtsqa_development",
        "agent_version": AGENT_VERSION,
        "agent_config": agent_config,
    }

    client = initialize_langfuse()

    try:
        with client.start_as_current_observation(
            as_type="span",
            name="kg-agent-question",
        ) as span:
            span.update(
                input={"question": sample["question"]},
                metadata=metadata,
            )

            trace_id = client.get_current_trace_id()
            print(f"Langfuse trace ID: {trace_id}")

            callback = create_langfuse_callback()

            result = run_agent(
                sample=sample,
                agent_config=agent_config,
                runnable_config={
                    "callbacks": [callback],
                    "run_name": AGENT_VERSION,
                    "metadata": {
                        "sample_id": str(SAMPLE_ID),
                        "agent_version": AGENT_VERSION,
                    },
                },
            )

            span.update(output=result)

            print(
                "Agent result:",
                json.dumps(result, ensure_ascii=False),
            )
    finally:
        client.shutdown()


if __name__ == "__main__":
    main()