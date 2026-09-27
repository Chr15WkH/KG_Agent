"""Validate and synchronize selected GTSQA dataset items."""

from langfuse.api import NotFoundError

from Evaluation.gtsqa_data import load_sample, load_gold
from Evaluation.evaluators import normalize_entity_answers


def prepare_local_items(*, dataset_name, sample_ids):
    """Validate selected GTSQA samples and prepare upload payloads."""

    if not isinstance(dataset_name, str) or not dataset_name.strip():
        raise ValueError("Dataset name must be a non-empty string.")

    sample_ids = tuple(sample_ids)

    # Validate that the sample selection is non-empty, integer-only, and unique.
    if not sample_ids:
        raise ValueError("Select at least one sample ID.")

    if any(type(sample_id) is not int for sample_id in sample_ids):
        raise ValueError("Sample IDs must be integers.")

    if len(sample_ids) != len(set(sample_ids)):
        raise ValueError("Duplicate sample IDs are not allowed.")

    prepared_items = []

    # Load each sample and verify that its question is valid and matches the Gold data.
    for sample_id in sample_ids:
        sample = load_sample(sample_id)
        gold = load_gold(sample_id)

        question = sample.get("question")

        if not isinstance(question, str) or not question.strip():
            raise ValueError(
                f"Invalid question for sample {sample_id}."
            )

        if question != gold["question"]:
            raise ValueError(
                f"Question mismatch for sample {sample_id}."
            )

        graph = sample.get("graph")

        # Verify that the sample has a non-empty graph of valid string triples.
        if not isinstance(graph, list) or not graph:
            raise ValueError(
                f"Sample {sample_id} must contain a non-empty graph."
            )

        for index, triple in enumerate(graph):
            if (
                not isinstance(triple, list)
                or len(triple) != 3
                or not all(
                    isinstance(value, str) and value.strip()
                    for value in triple
                )
            ):
                raise ValueError(
                    f"Invalid triple in sample {sample_id} "
                    f"at index {index}."
                )

        # Validate the Gold format without changing its stored representation.
        normalize_entity_answers(gold["gold_answer"])

        prepared_items.append(
            {
                "id": f"{dataset_name}-{sample_id}",
                "input": question,
                "expected_output": gold["gold_answer"],
                "metadata": {
                    "sample_id": sample_id,
                },
            }
        )

        # Keep only the small upload payload between samples.
        del graph, sample

    return prepared_items

def validate_remote_item(item, payload):
    """Reject conflicting items while allowing unrelated metadata."""

    differences = []

    if item.status != "ACTIVE":
        differences.append("status")

    if item.input != payload["input"]:
        differences.append("input")

    if item.expected_output != payload["expected_output"]:
        differences.append("expected_output")

    metadata = item.metadata or {}

    if str(metadata.get("sample_id")) != str(
        payload["metadata"]["sample_id"]
    ):
        differences.append("metadata.sample_id")

    if differences:
        raise ValueError(
            f"Dataset item {payload['id']} conflicts with local data: "
            f"{', '.join(differences)}. No overwrite was requested."
        )


def prepare_dataset(
    *,
    client,
    dataset_name,
    sample_ids,
    sync_missing_items=False,
):
    """Validate selected items, optionally create missing ones, and return them."""

    # Validate all local samples before making any remote changes.
    payloads = prepare_local_items(
        dataset_name=dataset_name,
        sample_ids=sample_ids,
    )

    try:
        dataset = client.get_dataset(dataset_name)
    except NotFoundError:
        if not sync_missing_items:
            raise ValueError(
                f"Dataset {dataset_name!r} does not exist "
                "and synchronization is disabled."
            ) from None

        client.create_dataset(
            name=dataset_name,
            description=(
                "GTSQA development experiments. "
                "Full graphs remain local. Not a held-out test set."
            ),
            metadata={
                "source_dataset": "GTSQA",
                "subset": "development",
            },
        )
        dataset = client.get_dataset(dataset_name)
        print(f"Created dataset: {dataset_name}", flush=True)

    existing_items = {
        item.id: item
        for item in dataset.items
    }

    missing_payloads = []

    # Check every selected existing item before creating missing items.
    for payload in payloads:
        existing_item = existing_items.get(payload["id"])

        if existing_item is None:
            missing_payloads.append(payload)
        else:
            validate_remote_item(existing_item, payload)

    if missing_payloads and not sync_missing_items:
        missing_ids = [
            payload["id"]
            for payload in missing_payloads
        ]
        raise ValueError(
            f"Selected items are missing: {missing_ids}. "
            "Synchronization is disabled."
        )

    for payload in missing_payloads:
        client.create_dataset_item(
            dataset_name=dataset_name,
            id=payload["id"],
            input=payload["input"],
            expected_output=payload["expected_output"],
            metadata=payload["metadata"],
        )
        print(f"Created dataset item: {payload['id']}", flush=True)

    # Reload and verify the items that will actually be used.
    dataset = client.get_dataset(dataset_name)
    refreshed_items = {
        item.id: item
        for item in dataset.items
    }

    selected_items = []

    for payload in payloads:
        item = refreshed_items.get(payload["id"])

        if item is None:
            raise ValueError(
                f"Selected item {payload['id']} is not available "
                "after preparation. Experiment will not start."
            )

        validate_remote_item(item, payload)
        selected_items.append(item)

    print(
        f"Dataset ready: {dataset_name} | "
        f"Selected: {len(selected_items)} | "
        f"Created: {len(missing_payloads)}",
        flush=True,
    )

    return selected_items