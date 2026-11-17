"""Sample GTSQA development/test questions by graph structure.

Builds one eligible pool from Dataset/gtsqa_without_graphs_test.parquet and
tops up the chosen split in Dataset/splits/gtsqa_splits.json to the
per-structure quota, using a fixed seed. IDs already in either split are
kept and never drawn again, so development and test cannot overlap.

A question is eligible when:
  - its graph isomorphism is one of STRUCTURES;
  - redundant is false;
  - all_answers_wikikg2 holds exactly one answer;
  - full_answer_subgraph_wikikg2 is not empty;
  - check_minimal_evidence passes: the SPARQL query on the Gold evidence
    returns the Gold answer, and no single evidence triple can be removed.

Run from the project root:
    python Dataset/build_gtsqa_splits.py --split development            # dry run
    python Dataset/build_gtsqa_splits.py --split development --write

Requires:
    pyarrow, rdflib
"""

import argparse
import random
import sys
from collections import Counter
from datetime import date

from build_gtsqa_gold import (
    MANIFEST_PATH,
    SOURCE_PATH,
    SPLITS,
    load_source_rows,
    make_gold_record,
    read_json,
    serialize,
    write_atomic,
)
from check_minimal_evidence import check_question


SEED = 20261117

FOUR_EDGE = ("(4)", "(3)(1)", "(2)(2)", "((2)(1))", "((1)(1))(1)", "(2(1)(1))")
SMALL = ("(1)", "(2)", "(1)(1)", "(3)")
STRUCTURES = FOUR_EDGE + SMALL

QUOTAS = {
    "development": {**{s: 5 for s in FOUR_EDGE}, **{s: 2 for s in SMALL}},
    "test": {**{s: 18 for s in FOUR_EDGE}, **{s: 10 for s in SMALL}},
}

CRITERIA = [
    "graph_isomorphism in the listed structures",
    "redundant is false",
    "exactly one answer in all_answers_wikikg2",
    "non-empty full_answer_subgraph_wikikg2",
    "check_minimal_evidence.py status PASS",
]


def exclusion_reason(row):
    """Return None for an eligible question, otherwise a short reason.

    Cheap checks run first; the SPARQL minimality check runs last.
    """
    if row["redundant"] is not False:
        return "redundant"

    answers = row["all_answers_wikikg2"]
    if not answers:
        return "no answer"
    if len(answers) != 1:
        return "more than one answer"

    if not row["full_answer_subgraph_wikikg2"]:
        return "empty evidence"

    try:
        result = check_question(make_gold_record(row))
    except Exception:  # Errors never count as passed.
        return "minimality ERROR"

    if result["status"] != "PASS":
        return f"minimality {result['status']}"

    return None


def test_type_label(row):
    value = row.get("test_type")
    if isinstance(value, (list, tuple)):
        return "+".join(sorted(value)) or "-"
    return str(value)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--split", choices=SPLITS, required=True)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    manifest = read_json(MANIFEST_PATH)
    if manifest.get("dataset_type") != "gtsqa":
        raise ValueError(f"{MANIFEST_PATH.name} is not a GTSQA manifest.")

    split_ids = list(manifest["splits"][args.split]["sample_ids"])
    used = {i for split in SPLITS for i in manifest["splits"][split]["sample_ids"]}

    rows = load_source_rows()

    unknown = sorted(i for i in used if i not in rows)
    if unknown:
        raise ValueError(f"Manifest IDs not in the source file: {unknown}")

    by_structure = {s: [] for s in STRUCTURES}
    for row in rows.values():
        if row["graph_isomorphism"] in by_structure:
            by_structure[row["graph_isomorphism"]].append(row)

    empty = [s for s, structure_rows in by_structure.items() if not structure_rows]
    if empty:
        raise ValueError(f"No source questions for structures: {empty}")

    print(f"Checking {sum(map(len, by_structure.values()))} candidate questions "
          f"in {len(STRUCTURES)} structures ...")
    reasons = {
        row["id"]: exclusion_reason(row)
        for structure_rows in by_structure.values()
        for row in structure_rows
    }

    # Questions already chosen must meet the same criteria as new ones.
    problems = []
    for sample_id in sorted(used):
        structure = rows[sample_id]["graph_isomorphism"]
        if structure not in by_structure:
            problems.append(f"{sample_id}: structure {structure} not in STRUCTURES")
        elif reasons[sample_id] is not None:
            problems.append(f"{sample_id}: {reasons[sample_id]}")
    if problems:
        print("\nQuestions already in the manifest fail the criteria:")
        for problem in problems:
            print(f"  {problem}")
        print("Nothing written.")
        sys.exit(1)

    quotas = QUOTAS[args.split]
    total_quotas = {s: sum(QUOTAS[x][s] for x in SPLITS) for s in STRUCTURES}
    new_ids = []
    shortages = []

    for structure in STRUCTURES:
        structure_rows = by_structure[structure]
        eligible = sorted(r["id"] for r in structure_rows if reasons[r["id"]] is None)
        excluded = Counter(
            reasons[r["id"]] for r in structure_rows if reasons[r["id"]] is not None
        )
        types = Counter(test_type_label(rows[i]) for i in eligible)

        current = [i for i in split_ids if rows[i]["graph_isomorphism"] == structure]
        need = quotas[structure] - len(current)
        candidates = [i for i in eligible if i not in used]

        print(f"\n{structure}")
        print(f"  source {len(structure_rows)}, eligible {len(eligible)} "
              f"({', '.join(f'{k} {v}' for k, v in sorted(types.items()))})")
        if excluded:
            print("  excluded: "
                  + ", ".join(f"{k} {v}" for k, v in excluded.most_common()))
        print(f"  in {args.split} now {len(current)}, quota {quotas[structure]}, "
              f"unused eligible {len(candidates)}")

        if need < 0:
            raise ValueError(f"{structure}: {args.split} already exceeds its quota.")

        if len(candidates) < need:
            shortages.append(f"{structure}: need {need}, only {len(candidates)}")
            continue

        rng = random.Random(f"{SEED}:{args.split}:{structure}")
        picked = sorted(rng.sample(candidates, need))
        new_ids.extend(picked)
        for i in picked:
            print(f"  + {i:<7} {test_type_label(rows[i])}")

        # Warn early if development and test together will not fit.
        if len(eligible) < total_quotas[structure]:
            print(f"  WARNING: both splits need {total_quotas[structure]} in total, "
                  f"the eligible pool has only {len(eligible)}.")

    if shortages:
        print("\nNot enough eligible questions:")
        for shortage in shortages:
            print(f"  {shortage}")
        print("Nothing written.")
        sys.exit(1)

    print(f"\n{args.split}: keep {len(split_ids)}, add {len(new_ids)}, "
          f"total {len(split_ids) + len(new_ids)}")

    if not new_ids:
        print("Split already complete; nothing written.")
        return

    if not args.write:
        print("Dry run only. Re-run with --write to save.")
        return

    manifest["splits"][args.split]["sample_ids"] = split_ids + new_ids
    sampling = manifest.setdefault("sampling", {})
    sampling[args.split] = {
        "date": date.today().isoformat(),
        "source": SOURCE_PATH.name,
        "seed": SEED,
        "quota_per_structure": quotas,
        "criteria": CRITERIA,
        "kept_existing": len(split_ids),
        "added": len(new_ids),
    }
    write_atomic(MANIFEST_PATH, serialize(manifest))

    print(f"Wrote {len(split_ids) + len(new_ids)} {args.split} IDs "
          f"to {MANIFEST_PATH.name}")


if __name__ == "__main__":
    main()
