import json
import logging
from ark_v1.ark_v1 import ARK_V1
from pathlib import Path
from dotenv import load_dotenv
from ark_v1.data_models.agent_models import QuestionTypes
from ark_v1.adapters.gtsqa import adapt_gtsqa_sample


# Choose the dataset and question.
DATASET = "gtsqa"  # "example" or "gtsqa"
SAMPLE_ID = 13311

EXAMPLES_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = Path(__file__).resolve().parents[3]

ENV_PATH = EXAMPLES_DIR.parent / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def load_sample():
    if DATASET == "example":
        path = EXAMPLES_DIR / "example_data.json"

        with path.open("r", encoding="utf-8") as file:
            sample = json.load(file)

        return sample, QuestionTypes.YES_NO

    if DATASET == "gtsqa":
        path = PROJECT_ROOT / "Dataset" / "gtsqa_development_agent_input.jsonl"

        with path.open("r", encoding="utf-8") as file:
            for line in file:
                sample = json.loads(line)

                if sample["id"] == SAMPLE_ID:
                    return (
                        adapt_gtsqa_sample(sample),
                        QuestionTypes.ENTITY_LIST,
                    )

        raise ValueError(f"GTSQA sample {SAMPLE_ID} was not found.")

    raise ValueError(f"Unsupported dataset: {DATASET}")


def main():
    config = {
        "llm": {
            "model": "deepseek/deepseek-chat",
            "temperature": 0,
            "top_p": 0.95,
        },
        # "max_reasoning_steps": 8, default is 8
        # "max_attempts": 5, default is 5
        # "recursion_limit": 200, default is 200
    }

    sample, question_type = load_sample()

    logging.info(
        "Dataset=%s, sample_id=%s, triples=%s",
        DATASET,
        sample.get("id", "example"),
        len(sample["graph"]),
    )
    logging.info("Question: %s", sample["question"])

    agent = ARK_V1()
    agent.load_configuration(config=config)
    agent.load_graph_data(sample["graph"])

    agent.set_initial_state(
        question=sample["question"],
        question_type=question_type,
    )

    final_state = agent.run()

    if final_state is None or final_state.get("finalAnswer") is None:
        raise RuntimeError("Agent finished without a final answer.")

    final_answer = final_state["finalAnswer"]

    if "answer" not in final_answer:
        raise RuntimeError("The returned final answer is missing 'answer'.")

    logging.info("Final answer: %s", final_answer["answer"])


if __name__ == "__main__":
    main()