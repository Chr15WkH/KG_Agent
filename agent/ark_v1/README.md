# ARK-V1

ARK-V1 is our first version of a KG-Agent which explores a KG to answer natural language questions.

## Install

Install the agent using pip. E.g in a new conda environment:

```bash
conda create -n myenv python=3.11
conda activate myenv
pip install -e .
```

## Run the example

Test the agent by running a small example using a local qwen3:14b model:
#### Using a local Ollama model
```bash
python examples/minimal_ollama.py qwen3:14b
```

## Cite our work
Link to the corresponding paper: [Link](https://arxiv.org/abs/2509.18063)
```bash
@article{klein2025ark,
  title={ARK-V1: An LLM-Agent for Knowledge Graph Question Answering Requiring Commonsense Reasoning},
  author={Klein, Jan-Felix and Ohnemus, Lars},
  journal={arXiv preprint arXiv:2509.18063},
  year={2025}
}
```

## Local Evaluation Adaptations

This upstream ARK-V1 baseline includes the following local changes:

1. Model access: Added LiteLLM support, registered deepseek/deepseek-chat for OpenRouter.
2. Dependencies: Added langchain-litellm to pyproject.toml.
3. Execution interface: Added runnable_config for callbacks and metadata, and verbose to control printed messages.
4. Evaluation: Added Evaluation/adapters/ark_v1.py for CRLT Boolean tasks, reusing the existing evaluators.
5. Prompt roles: Changed the five non-system-description templates from system to user messages.
6. Stream completion: Return the collected answer after the event stream finishes.

Prompt text, reasoning routes, retry conditions, and final-answer extraction remain unchanged by these adaptations.
