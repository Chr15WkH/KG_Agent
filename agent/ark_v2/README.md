# ARK v2

This is the initial ARK v2 development copy of the project's previous locally adapted agent, with package and class names updated and algorithmic behavior preserved. It is based on upstream ARK-V1 (https://github.com/JaFeKl/ark_v1). It includes dataset integration, graph-access changes and evaluation support. It is not an unmodified upstream baseline. The original license and citation are retained below.

## Install

Follow the [root README](../../README.md#installation) to create the shared environment and install project dependencies. Then register this Agent from the KG_Agent project root:

```bash
source .venv/bin/activate
python -m pip install --no-deps -e agent/ark_v2
```

The Python package is `ark_v2` and its class is `ARK_V2`. All dependencies are shared through `KG_Agent/.venv`; no separate Agent environment is needed. Evaluation and the LiteLLM/OpenRouter examples read shared configuration from `KG_Agent/.env`.

## Run an Example

From the KG_Agent project root, activate the shared environment and enter the Agent directory:

```bash
source .venv/bin/activate
cd agent/ark_v2
```

Review the dataset and sample settings in `examples/minimal_litellm.py`, then run it with a model supported by the configured LiteLLM service:

```bash
python examples/minimal_litellm.py qwen3.5:9b
```

An Ollama example is also available. It requires a running Ollama service and the model configured in the script:

```bash
python examples/minimal_ollama.py qwen3:14b
```

## Upstream Citation

Original ARK-V1 paper: [ARK-V1](https://arxiv.org/abs/2509.18063).

```bash
@article{klein2025ark,
  title={ARK-V1: An LLM-Agent for Knowledge Graph Question Answering Requiring Commonsense Reasoning},
  author={Klein, Jan-Felix and Ohnemus, Lars},
  journal={arXiv preprint arXiv:2509.18063},
  year={2025}
}
```
