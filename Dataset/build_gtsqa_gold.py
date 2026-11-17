"""Build the GTSQA Gold file of one split from the split manifest.

Every Gold record is generated from Dataset/gtsqa_without_graphs_test.parquet
in the format of the existing development Gold file.

Records already in the Gold file are never rewritten. Each one must be
identical to its regenerated version; otherwise nothing is written. Manifest
IDs that are not yet in the file are appended in manifest order.

Run from the project root:
    python Dataset/build_gtsqa_gold.py --split development            # dry run
    python Dataset/build_gtsqa_gold.py --split development --write

Requires:
    pyarrow
"""

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

import pyarrow.parquet as pq


DATASET_DIR = Path(__file__).resolve().parent
SOURCE_PATH = DATASET_DIR / "gtsqa_without_graphs_test.parquet"
MANIFEST_PATH = DATASET_DIR / "splits" / "gtsqa_splits.json"

SPLITS = ("development", "test")
GOLD_PATHS = {
    "development": DATASET_DIR / "gtsqa_development_gold.json",
    "test": DATASET_DIR / "gtsqa_test_gold.json",
}

FIELD_DEFINITIONS = {
    "redundant": {
        "description": (
            "Whether the question can be answered using only a proper "
            "subset of its seed entities."
        ),
        "true": (
            "At least one seed entity or its corresponding condition is "
            "unnecessary for answering the question."
        ),
        "false": (
            "All seed entities and their corresponding conditions are "
            "necessary for answering the question."
        ),
    }
}


def read_json(path):
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def serialize(data):
    """The on-disk format of the Gold and manifest files."""
    return json.dumps(data, ensure_ascii=False, indent=2) + "\n"


def write_atomic(path, text):
    """Write a complete temporary file first, then replace the target."""
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    ) as file:
        file.write(text)
        temp_path = Path(file.name)

    os.replace(temp_path, path)


def load_source_rows(path=SOURCE_PATH):
    """Return {question ID: source row} for the GTSQA test split."""
    rows = {}

    for row in pq.read_table(path).to_pylist():
        if row["id"] in rows:
            raise ValueError(f"Duplicate source ID: {row['id']}.")
        rows[row["id"]] = row

    return rows


def load_split_ids(split, manifest_path=MANIFEST_PATH):
    manifest = read_json(manifest_path)
    if manifest.get("dataset_type") != "gtsqa":
        raise ValueError(f"{manifest_path.name} is not a GTSQA manifest.")

    ids = manifest["splits"][split]["sample_ids"]
    if len(ids) != len(set(ids)):
        raise ValueError(f"Split {split!r} contains duplicate IDs.")

    return ids


def make_gold_record(row):
    """Insertion order defines the saved field order."""
    return {
        "id": row["id"],
        "question_profile": {
            "question": row["question"],
            "n_hops": row["n_hops"],
            "graph_isomorphism": row["graph_isomorphism"],
            "redundant": row["redundant"],
        },
        "generation_reference": {
            "answer_node": row["answer_node"],
            "answer_subgraph": [list(t) for t in row["answer_subgraph"]],
            "sparql_query": row["sparql_query"],
        },
        "entity_linking_gold": {
            "seed_entities": list(row["seed_entities"]),
        },
        "evaluation_gold": {
            "all_answers_wikikg2": list(row["all_answers_wikikg2"]),
            "full_answer_subgraph_wikikg2": [
                list(t) for t in row["full_answer_subgraph_wikikg2"]
            ],
        },
    }


def first_difference(old, new, path="record"):
    """Describe the first place where two JSON values differ."""
    if type(old) is not type(new):
        return f"{path}: type {type(old).__name__} != {type(new).__name__}"

    if isinstance(old, dict):
        if list(old) != list(new):
            return f"{path}: keys {list(old)} != {list(new)}"
        for key in old:
            difference = first_difference(old[key], new[key], f"{path}.{key}")
            if difference:
                return difference
        return None

    if isinstance(old, list):
        if len(old) != len(new):
            return f"{path}: length {len(old)} != {len(new)}"
        for index, (a, b) in enumerate(zip(old, new)):
            difference = first_difference(a, b, f"{path}[{index}]")
            if difference:
                return difference
        return None

    if old != new:
        return f"{path}: {old!r} != {new!r}"

    return None


def new_gold_file(split):
    return {
        "dataset_info": {
            "dataset_name": "GTSQA",
            "source_split": "test",
            "knowledge_graph": "ogbl-wikikg2",
            "subset_name": split,
            "number_of_questions": 0,
        },
        "field_definitions": FIELD_DEFINITIONS,
        "questions": [],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--split", choices=SPLITS, required=True)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    split_ids = load_split_ids(args.split)
    rows = load_source_rows()

    unknown = [i for i in split_ids if i not in rows]
    if unknown:
        raise ValueError(f"Split IDs not in the source file: {unknown}")

    gold_path = GOLD_PATHS[args.split]

    if gold_path.exists():
        text = gold_path.read_text(encoding="utf-8")
        data = json.loads(text)

        # Rewriting must leave the existing part byte-for-byte unchanged.
        if serialize(data) != text:
            raise ValueError(
                f"{gold_path.name} is not in the expected JSON layout; "
                "refusing to rewrite it."
            )
        if data["dataset_info"].get("subset_name") != args.split:
            raise ValueError(f"{gold_path.name} is not the {args.split} Gold.")
    else:
        data = new_gold_file(args.split)

    existing = data["questions"]
    existing_ids = [record["id"] for record in existing]

    if existing_ids != split_ids[:len(existing_ids)]:
        raise ValueError(
            f"{gold_path.name} must hold a prefix of the {args.split} split, "
            "in manifest order."
        )

    mismatches = []
    for record in existing:
        regenerated = make_gold_record(rows[record["id"]])
        if serialize(regenerated) != serialize(record):
            mismatches.append(
                (record["id"], first_difference(record, regenerated))
            )

    print(f"Gold file:         {gold_path.name}")
    print(f"Split IDs:         {len(split_ids)}")
    print(f"Existing records:  {len(existing)}")

    if mismatches:
        print("\nExisting records differ from their regenerated version:")
        for sample_id, difference in mismatches:
            print(f"  {sample_id}: {difference}")
        print("Nothing written.")
        sys.exit(1)

    if existing:
        print("Existing records:  all identical to the regenerated version")

    new_records = [make_gold_record(rows[i]) for i in split_ids[len(existing):]]
    print(f"Records to append: {len(new_records)}")
    for record in new_records:
        profile = record["question_profile"]
        print(f"  {record['id']:<7} {profile['graph_isomorphism']:<13} "
              f"{profile['question'][:80]}")

    if not new_records:
        print("Gold file already up to date; nothing written.")
        return

    if not args.write:
        print("Dry run only. Re-run with --write to save.")
        return

    data["questions"].extend(new_records)
    data["dataset_info"]["number_of_questions"] = len(data["questions"])
    write_atomic(gold_path, serialize(data))

    print(f"Wrote {len(data['questions'])} records to {gold_path.name}")


if __name__ == "__main__":
    main()
