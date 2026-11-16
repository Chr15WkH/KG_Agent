"""
Resolve development/test sample selections from fixed split manifests.
Each dataset type has one manifest in Dataset/splits/. A manifest lists the
sample IDs of every split and the Langfuse dataset that holds those items.
Sample IDs are dataset sample IDs (e.g. 13311, "13311-ua-01", "S2"),
not Langfuse item IDs.
"""

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SPLIT_DIR = PROJECT_ROOT / "Dataset" / "splits"

SPLIT_FILES = {
    "gtsqa": "gtsqa_splits.json",
    "gtsqa_ua": "gtsqa_ua_splits.json",
    "crlt": "crlt_splits.json",
}
SUPPORTED_SPLITS = ("development", "test")


def _validate_sample_id(dataset_type: str, sample_id) -> None:
    """GTSQA uses integer IDs; GTSQA_UA and CRLT use non-empty strings."""
    if dataset_type == "gtsqa":
        # bool is a subclass of int and must not pass as a sample ID.
        if type(sample_id) is not int:
            raise ValueError(
                f"GTSQA sample IDs must be integers, got {sample_id!r}."
            )
    elif not isinstance(sample_id, str) or not sample_id.strip():
        raise ValueError(
            f"{dataset_type} sample IDs must be non-empty strings, "
            f"got {sample_id!r}."
        )


def load_split_manifest(dataset_type: str) -> dict:
    """Load and validate the split manifest of one dataset type."""
    if dataset_type not in SPLIT_FILES:
        raise ValueError(f"Unsupported dataset type: {dataset_type}")

    manifest_path = SPLIT_DIR / SPLIT_FILES[dataset_type]

    with manifest_path.open("r", encoding="utf-8") as file:
        manifest = json.load(file)

    if manifest.get("dataset_type") != dataset_type:
        raise ValueError(
            f"{manifest_path.name} declares dataset_type "
            f"{manifest.get('dataset_type')!r}, expected {dataset_type!r}."
        )

    splits = manifest.get("splits")
    if not isinstance(splits, dict) or set(splits) != set(SUPPORTED_SPLITS):
        raise ValueError(
            f"{manifest_path.name} must define exactly the splits "
            f"{SUPPORTED_SPLITS}."
        )

    seen = {}

    for split_name, split in splits.items():
        dataset_name = split.get("langfuse_dataset")
        sample_ids = split.get("sample_ids")

        if not isinstance(dataset_name, str) or not dataset_name.strip():
            raise ValueError(
                f"{manifest_path.name}: split {split_name!r} needs a "
                "non-empty langfuse_dataset."
            )

        if not isinstance(sample_ids, list):
            raise ValueError(
                f"{manifest_path.name}: split {split_name!r} needs a "
                "sample_ids list."
            )

        for sample_id in sample_ids:
            _validate_sample_id(dataset_type, sample_id)

            # Rejects duplicates within a split and overlap between splits.
            if sample_id in seen:
                raise ValueError(
                    f"{manifest_path.name}: sample {sample_id!r} appears in "
                    f"{seen[sample_id]!r} and {split_name!r}."
                )
            seen[sample_id] = split_name

    return manifest


def resolve_selection(dataset_type: str, split: str, sample_ids=None) -> dict:
    """
    Return the Langfuse dataset name and the ordered sample IDs to run.
    sample_ids=None selects the whole split in manifest order.
    A tuple or list selects only those samples, in the given order;
    every ID must belong to the chosen split.
    """
    if split not in SUPPORTED_SPLITS:
        raise ValueError(
            f"Unsupported split: {split!r}. Choose one of {SUPPORTED_SPLITS}."
        )

    manifest = load_split_manifest(dataset_type)
    split_info = manifest["splits"][split]
    split_ids = split_info["sample_ids"]

    if not split_ids:
        raise ValueError(
            f"The {split!r} split of {dataset_type} is not defined yet "
            f"(empty sample_ids in {SPLIT_FILES[dataset_type]})."
        )

    if sample_ids is None:
        selected = tuple(split_ids)
        selection_mode = "full_split"
    else:
        if isinstance(sample_ids, (str, int)):
            raise ValueError(
                "SAMPLE_IDS must be None or a tuple/list of IDs, "
                "e.g. (13311,) or ('S2',)."
            )

        selected = tuple(sample_ids)

        if not selected:
            raise ValueError("SAMPLE_IDS is empty; use None for the whole split.")

        if len(selected) != len(set(selected)):
            raise ValueError("Duplicate sample IDs are not allowed.")

        split_id_set = set(split_ids)

        for sample_id in selected:
            _validate_sample_id(dataset_type, sample_id)

            if sample_id not in split_id_set:
                raise ValueError(
                    f"Sample {sample_id!r} is not in the {split!r} split "
                    f"of {dataset_type}."
                )

        selection_mode = "manual"

    return {
        "dataset_name": split_info["langfuse_dataset"],
        "split": split,
        "sample_ids": selected,
        "selection_mode": selection_mode,
    }
