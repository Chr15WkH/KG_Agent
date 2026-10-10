# KG Agent Evaluation

A framework for developing and evaluating knowledge graph agents with shared dependencies and evaluation workflows.

## Installation

Use Python 3.11. Run the following commands from the KG_Agent project root.

Create and activate the shared virtual environment:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

Install the project and its dependencies from the root `pyproject.toml`:

```bash
python -m pip install -e .
```

Register the adapted Agent in the same environment:

```bash
python -m pip install --no-deps -e agent/ark_v1_1
```

All Agents use the root `.venv`; separate Agent environments are unnecessary. Installation is required for initial setup or environment recreation, not for each run. Ordinary edits to Agent source code are available through the editable installation without reinstalling.

## Configuration

Configure model-service credentials, endpoints and Langfuse settings in the root `.env` file. Evaluation and the LiteLLM/OpenRouter examples load this shared file.

## Run an Evaluation

Activate the environment from the project root in each new terminal session:

```bash
source .venv/bin/activate
```

Review the Agent, model, dataset and sample settings in `Evaluation/run_experiment.py`, then run:

```bash
python -m Evaluation.run_experiment
```

Evaluation calls the configured model service and records experiment results in Langfuse.

See the [ARK v1.1 README](agent/ark_v1_1/README.md) for standalone Agent examples.
