"""Prepare a single-item Langfuse development dataset."""

from pathlib import Path

from dotenv import load_dotenv
from langfuse.api import NotFoundError

from Evaluation.gtsqa_data import load_sample, load_gold
from Evaluation.langfuse_support import initialize_langfuse


PROJECT_ROOT = Path(__file__).resolve().parents[1]

ENV_FILE = PROJECT_ROOT / "agent" / "ark_v1" / ".env"
DATASET_NAME = "gtsqa-development"
SAMPLE_ID = 13311
ITEM_ID = f"{DATASET_NAME}-{SAMPLE_ID}"


def main() -> None:
    if not ENV_FILE.is_file():
        raise FileNotFoundError(
            f"Environment file not found: {ENV_FILE}"
        )

    load_dotenv(ENV_FILE, override=True)

    sample = load_sample(SAMPLE_ID)
    gold = load_gold(SAMPLE_ID)

    if sample["question"].strip() != gold["question"].strip():
        raise ValueError(
            f"Question mismatch for sample {SAMPLE_ID}."
        )

    item_metadata = {
        "sample_id": SAMPLE_ID,
        "dataset_version": DATASET_NAME,
    }

    client = initialize_langfuse()

    try:
        try:
            dataset = client.get_dataset(DATASET_NAME)
        except NotFoundError:
            client.create_dataset(
                name=DATASET_NAME,
                description=(
                    "Single-item GTSQA development pilot. "
                    "Graphs remain local. Not a held-out test set."
                ),
                metadata={
                    "source_dataset": "GTSQA",
                    "subset": "development",
                },
            )
            dataset = client.get_dataset(DATASET_NAME)
            print(f"Created dataset: {DATASET_NAME}")

        existing_item = next(
            (item for item in dataset.items if item.id == ITEM_ID),
            None,
        )

        # This pilot is intentionally limited to one known item.
        unexpected_items = [
            item.id
            for item in dataset.items
            if item.id != ITEM_ID
        ]

        if unexpected_items:
            raise ValueError(
                "Dataset contains unexpected items. "
                f"No items were changed: {unexpected_items}"
            )

        if existing_item is not None:
            matches = (
                existing_item.input == sample["question"]
                and existing_item.expected_output == gold["gold_answer"]
                and existing_item.metadata == item_metadata
                and existing_item.status == "ACTIVE"
            )

            if not matches:
                raise ValueError(
                    "Existing dataset item differs from local data "
                    "or is not ACTIVE. No item was overwritten."
                )

            print(f"Dataset item already matches: {ITEM_ID}")
            return

        created_item = client.create_dataset_item(
            dataset_name=DATASET_NAME,
            id=ITEM_ID,
            input=sample["question"],
            expected_output=gold["gold_answer"],
            metadata=item_metadata,
        )

        print(f"Created dataset item: {created_item.id}")
        print(f"Dataset ready: {DATASET_NAME}")

    finally:
        client.shutdown()


if __name__ == "__main__":
    main()