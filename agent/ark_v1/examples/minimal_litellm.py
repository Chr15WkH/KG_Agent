import sys
import os
import json
import logging
from ark_v1.ark_v1 import ARK_V1
from pathlib import Path
from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def main():
    if len(sys.argv) < 2:
        print("Usage: python examples/minimal_litellm.py <model_name>")
        sys.exit(1)

    model_name = sys.argv[1]
    print(f"Using model: {model_name}")

    config = {
        "llm": {
            "model": model_name,
            "temperature": 0.9,
            "top_p": 0.9,
            "seed": 42,
        },
    }

    agent = ARK_V1()
    agent.load_configuration(config=config)

    # load example data
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "example_data.json"),
        "r",
    ) as file:
        example_data = json.load(file)

    agent.load_graph_data(example_data["graph"])
    agent.set_initial_state(question=example_data["question"])
    final_state = agent.run()

    logging.info(
        f"Final answer: {final_state.get('finalAnswer').get('answer', 'No answer found')}"
    )


if __name__ == "__main__":
    main()
