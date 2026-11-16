"""Freeze the CR-LT-KGQA test split from the existing Langfuse dataset.

Reads (never modifies) the Langfuse dataset, takes every ACTIVE item that is
not in the development split, and writes the IDs into
Dataset/splits/crlt_splits.json in natural order (S1, S2, ..., S200).

Run from the project root:
    python Dataset/build_crlt_splits.py            # dry run, prints a summary
    python Dataset/build_crlt_splits.py --write    # writes the test split
    python Dataset/build_crlt_splits.py --write --overwrite
                                                   # replaces an existing test split
"""

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv  # noqa: E402

from Evaluation.langfuse_support import initialize_langfuse  # noqa: E402


MANIFEST_PATH = PROJECT_ROOT / "Dataset" / "splits" / "crlt_splits.json"
ENV_FILE = PROJECT_ROOT / ".env"


def natural_key(item_id: str):
    """Sort S2 before S10; IDs without a number go last."""
    match = re.fullmatch(r"([A-Za-z]*)(\d+)", item_id)
    if match:
        return (0, match.group(1), int(match.group(2)))
    return (1, item_id, 0)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--write", action="store_true", help="write the test split")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="replace a non-empty test split",
    )
    args = parser.parse_args()

    with MANIFEST_PATH.open("r", encoding="utf-8") as file:
        manifest = json.load(file)

    dev_split = manifest["splits"]["development"]
    test_split = manifest["splits"]["test"]
    dataset_name = dev_split["langfuse_dataset"]

    if test_split["langfuse_dataset"] != dataset_name:
        raise ValueError("Development and test must use the same Langfuse dataset.")

    dev_ids = list(dev_split["sample_ids"])

    load_dotenv(ENV_FILE, override=True)
    client = initialize_langfuse()

    try:
        # Read-only: get_dataset pages through all items.
        dataset = client.get_dataset(dataset_name)
        items = list(dataset.items)
    finally:
        client.shutdown()

    all_ids = [item.id for item in items]
    active = [item for item in items if item.status == "ACTIVE"]
    active_ids = {item.id for item in active}

    missing_dev = [i for i in dev_ids if i not in active_ids]
    if missing_dev:
        raise ValueError(f"Development IDs not ACTIVE in Langfuse: {missing_dev}")

    non_boolean = [
        item.id for item in active if type(item.expected_output) is not bool
    ]
    unexpected_format = [
        item.id for item in active if not re.fullmatch(r"S\d+", item.id)
    ]

    test_ids = sorted(
        (i for i in active_ids if i not in set(dev_ids)),
        key=natural_key,
    )

    print(f"Langfuse dataset:      {dataset_name}")
    print(f"Items (all statuses):  {len(all_ids)}")
    print(f"ACTIVE items:          {len(active_ids)}")
    print(f"Development IDs:       {len(dev_ids)}")
    print(f"Test IDs (derived):    {len(test_ids)}")
    print(f"First / last test IDs: {test_ids[:3]} ... {test_ids[-3:]}")
    if non_boolean:
        print(f"WARNING non-Boolean expected_output: {non_boolean}")
    if unexpected_format:
        print(
            "WARNING IDs not of the form S<number> "
            f"(possibly not the StrategyQA-based QA subset): {unexpected_format}"
        )

    if not args.write:
        print("Dry run only. Re-run with --write to save the test split.")
        return

    if non_boolean:
        raise ValueError("Refusing to write: some items lack a Boolean answer.")

    if test_split["sample_ids"] and not args.overwrite:
        if test_split["sample_ids"] == test_ids:
            print("Test split already up to date; nothing written.")
            return
        raise ValueError(
            "Test split already exists and differs from Langfuse. "
            "Use --overwrite only if the change is intended."
        )

    test_split["sample_ids"] = test_ids
    manifest["generated_from"] = {
        "langfuse_dataset": dataset_name,
        "date": date.today().isoformat(),
        "active_items": len(active_ids),
        "development_items": len(dev_ids),
        "test_items": len(test_ids),
        "rule": "all ACTIVE items minus the development split, natural ID order",
    }

    with MANIFEST_PATH.open("w", encoding="utf-8") as file:
        json.dump(manifest, file, ensure_ascii=False, indent=2)
        file.write("\n")

    print(f"Wrote {len(test_ids)} test IDs to {MANIFEST_PATH.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
