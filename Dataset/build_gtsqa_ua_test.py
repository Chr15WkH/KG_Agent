"""Build the GTSQA_UA test set from the GTSQA test split.

For each graph structure, the GTSQA test questions of that structure are
shuffled with a fixed seed and tried in that order until PAIRS_PER_STRUCTURE
original/unanswerable pairs are built. Each pair is built exactly as for the
development set, by build_gtsqa_ua.build_pair. Questions without a valid
deletion of at most MAX_DELETE facts are skipped and recorded.

Writes Dataset/gtsqa_ua_test_gold.json and the test IDs in
Dataset/splits/gtsqa_ua_splits.json. Nothing is written if a structure ends
with fewer than PAIRS_PER_STRUCTURE pairs. An existing output file or a
non-empty test split is never overwritten.

Run from the project root (after the GTSQA test split is built):
    python Dataset/build_gtsqa_ua_test.py

Requires:
    pyarrow, rdflib
"""

import random
import sys

from build_gtsqa_gold import GOLD_PATHS, load_split_ids, read_json, serialize, write_atomic
from build_gtsqa_splits import SEED, STRUCTURES
from build_gtsqa_ua import DATASET_DIR, build_pair


INPUT_PATH = DATASET_DIR / "gtsqa_test_agent_input.jsonl"
GOLD_PATH = GOLD_PATHS["test"]
OUTPUT_PATH = DATASET_DIR / "gtsqa_ua_test_gold.json"
UA_MANIFEST_PATH = DATASET_DIR / "splits" / "gtsqa_ua_splits.json"

PAIRS_PER_STRUCTURE = 5
MAX_DELETE = 2


def main():
    if OUTPUT_PATH.exists():
        raise FileExistsError(f"{OUTPUT_PATH.name} already exists; not overwritten.")
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"{INPUT_PATH.name} missing; run extract_gtsqa_graphs.py --split test."
        )

    manifest_text = UA_MANIFEST_PATH.read_text(encoding="utf-8")
    manifest = read_json(UA_MANIFEST_PATH)
    if serialize(manifest) != manifest_text:
        raise ValueError(f"{UA_MANIFEST_PATH.name} is not in the expected layout.")
    if manifest["splits"]["test"]["sample_ids"]:
        raise ValueError(f"The test split in {UA_MANIFEST_PATH.name} is not empty.")

    test_ids = load_split_ids("test")
    gold_by_id = {q["id"]: q for q in read_json(GOLD_PATH)["questions"]}
    missing = [i for i in test_ids if i not in gold_by_id]
    if missing:
        raise ValueError(f"No GTSQA test Gold record for {missing}.")

    by_structure = {s: [] for s in STRUCTURES}
    for sample_id in test_ids:
        structure = gold_by_id[sample_id]["question_profile"]["graph_isomorphism"]
        if structure not in by_structure:
            raise ValueError(f"{sample_id}: unexpected structure {structure}.")
        by_structure[structure].append(sample_id)

    records = []
    skipped = []
    shortages = []

    for structure in STRUCTURES:
        candidates = by_structure[structure]
        rng = random.Random(f"{SEED}:ua-test:{structure}")
        order = rng.sample(candidates, len(candidates))
        built = 0

        print(f"\n{structure} ({len(candidates)} test questions)")
        for sample_id in order:
            if built == PAIRS_PER_STRUCTURE:
                break
            try:
                pair = build_pair(gold_by_id[sample_id], MAX_DELETE, INPUT_PATH)
            except Exception as error:  # Failed builds never become UA labels.
                skipped.append({
                    "id": str(sample_id),
                    "graph_isomorphism": structure,
                    "status": "needs_review",
                    "error": f"{type(error).__name__}: {error}",
                })
                print(f"  {sample_id}: skipped — {error}")
                continue

            records.extend(pair)
            built += 1
            removed = len(pair[1]["modification"]["removed_triples"])
            print(f"  {sample_id}: passed — deleted {removed} fact(s)")

        if built < PAIRS_PER_STRUCTURE:
            shortages.append(f"{structure}: {built} of {PAIRS_PER_STRUCTURE} pairs")

    if shortages:
        print("\nNot enough pairs:")
        for shortage in shortages:
            print(f"  {shortage}")
        print("Nothing written.")
        sys.exit(1)

    dataset = {
        "dataset_info": {
            "name": "gtsqa_ua_test",
            "source_agent_input": INPUT_PATH.name,
            "source_gold": GOLD_PATH.name,
            "construction_method": "controlled_fact_deletion",
            "candidate_order": "sorted_qid_pid_triples",
            "max_deleted_facts": MAX_DELETE,
            "pair_count": len(records) // 2,
            "item_count": len(records),
            "answerability_definition": (
                "The original query returns verified non-empty answers. "
                "A deleted variant is unanswerable when the same query "
                "executes successfully and returns no answers."
            ),
            "selection": {
                "source_split": "GTSQA test split (splits/gtsqa_splits.json)",
                "pairs_per_structure": PAIRS_PER_STRUCTURE,
                "structures": list(STRUCTURES),
                "seed": SEED,
                "rule": (
                    "Per structure, the test questions are shuffled with "
                    "random.Random(f'{seed}:ua-test:{structure}') and tried "
                    "in that order until the quota is reached; failed "
                    "builds are skipped and listed under 'skipped'."
                ),
            },
        },
        "questions": records,
        "skipped": skipped,
    }

    with OUTPUT_PATH.open("x", encoding="utf-8") as file:
        file.write(serialize(dataset))

    manifest["splits"]["test"]["sample_ids"] = [record["id"] for record in records]
    write_atomic(UA_MANIFEST_PATH, serialize(manifest))

    print(f"\nSaved {len(records) // 2} pairs ({len(records)} items) to "
          f"{OUTPUT_PATH.name}; skipped {len(skipped)} question(s).")
    print(f"Wrote {len(records)} test IDs to {UA_MANIFEST_PATH.name}.")


if __name__ == "__main__":
    main()
