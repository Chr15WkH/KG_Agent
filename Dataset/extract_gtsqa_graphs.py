"""Extract the question graphs of one GTSQA split and verify them.

Reads the split IDs from Dataset/splits/gtsqa_splits.json and appends the
missing questions to the split's agent-input JSONL. Questions already in the
file are never rewritten.

Afterwards every question of the split is checked against its Gold record
(run build_gtsqa_gold.py first):
  - the question text equals the Gold question;
  - every Gold evidence triple is in the graph;
  - every seed entity and the Gold answer occur in the graph;
  - the SPARQL query on the full graph returns exactly the Gold answers.

Run from the project root:
    python Dataset/extract_gtsqa_graphs.py --split development
    python Dataset/extract_gtsqa_graphs.py --split development --verify-only

Requires:
    pyarrow, rdflib
"""

import argparse
import json
import sys

import pyarrow.parquet as pq

from build_gtsqa_gold import DATASET_DIR, GOLD_PATHS, SPLITS, load_split_ids, read_json
from build_gtsqa_ua import (
    execute_query,
    extract_id,
    make_graph,
    normalize_answers,
    normalize_triple,
)


SOURCE_PATH = DATASET_DIR / "gtsqa_with_graphs_test.parquet"
OUTPUT_PATHS = {
    "development": DATASET_DIR / "gtsqa_development_agent_input.jsonl",
    "test": DATASET_DIR / "gtsqa_test_agent_input.jsonl",
}


def read_output_ids(path):
    """IDs already in the JSONL file, in file order."""
    ids = []
    if not path.exists():
        return ids

    with path.open("r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                ids.append(json.loads(line)["id"])

    if len(ids) != len(set(ids)):
        raise ValueError(f"{path.name} contains duplicate IDs.")

    return ids


def ends_with_newline(path):
    if not path.exists() or path.stat().st_size == 0:
        return True
    with path.open("rb") as file:
        file.seek(-1, 2)
        return file.read(1) == b"\n"


def extract(target_ids, output_path):
    """Stream the source parquet and append the target questions."""
    targets = set(target_ids)
    found = set()
    source = pq.ParquetFile(SOURCE_PATH)

    with output_path.open("a", encoding="utf-8") as output_file:
        for batch in source.iter_batches(
            batch_size=1,
            columns=["id", "question", "graph"],
            use_threads=False,
        ):
            question_id = batch.column("id")[0].as_py()
            if question_id not in targets:
                continue

            question = batch.column("question")[0].as_py()
            graph = batch.column("graph")[0].as_py()

            if not question:
                raise RuntimeError(f"ID {question_id}: question is empty")
            if not graph:
                raise RuntimeError(f"ID {question_id}: graph is empty")

            record = {"id": question_id, "question": question, "graph": graph}
            output_file.write(json.dumps(record, ensure_ascii=False) + "\n")
            output_file.flush()

            found.add(question_id)
            print(f"Extracted {question_id}: {len(graph)} edges, "
                  f"{len(found)}/{len(targets)} questions")

            if found == targets:
                break

    missing = targets - found
    if missing:
        raise RuntimeError(f"Missing IDs in the source: {sorted(missing)}")


def check_sample(sample, gold):
    """Return a list of problems; an empty list means the sample passed."""
    problems = []

    if sample["question"] != gold["question_profile"]["question"]:
        problems.append("question differs from Gold")

    triples = {normalize_triple(t) for t in sample["graph"]}
    nodes = {t[0] for t in triples} | {t[2] for t in triples}

    evidence = {
        normalize_triple(t)
        for t in gold["evaluation_gold"]["full_answer_subgraph_wikikg2"]
    }
    absent = evidence - triples
    if absent:
        problems.append(f"{len(absent)} Gold evidence triple(s) not in graph")

    seeds = {
        extract_id(seed, "Q")
        for seed in gold["entity_linking_gold"]["seed_entities"]
    }
    if seeds - nodes:
        problems.append(f"seed(s) not in graph: {sorted(seeds - nodes)}")

    expected = normalize_answers(gold["evaluation_gold"]["all_answers_wikikg2"])
    if set(expected) - nodes:
        problems.append(f"answer not in graph: {sorted(set(expected) - nodes)}")

    query = gold["generation_reference"]["sparql_query"]
    found = execute_query(make_graph(triples), query)
    if found != expected:
        problems.append(f"query on full graph returns {found}, Gold is {expected}")

    return problems


def verify(split_ids, output_path, gold_by_id):
    remaining = set(split_ids)
    failed = 0

    with output_path.open("r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue
            sample = json.loads(line)
            if sample["id"] not in remaining:
                continue
            remaining.discard(sample["id"])

            try:
                problems = check_sample(sample, gold_by_id[sample["id"]])
            except Exception as error:  # Errors never count as passed.
                problems = [f"{type(error).__name__}: {error}"]

            failed += bool(problems)
            status = "FAIL" if problems else "PASS"
            print(f"{sample['id']:<7} {status}  {'; '.join(problems)}")

    if remaining:
        raise RuntimeError(f"IDs not in {output_path.name}: {sorted(remaining)}")

    print(f"\n{len(split_ids)} checked, {len(split_ids) - failed} passed, "
          f"{failed} failed")
    return failed == 0


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--split", choices=SPLITS, required=True)
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()

    split_ids = load_split_ids(args.split)
    output_path = OUTPUT_PATHS[args.split]
    gold_path = GOLD_PATHS[args.split]

    if not gold_path.exists():
        raise FileNotFoundError(f"{gold_path.name} missing; run build_gtsqa_gold.py.")
    gold_by_id = {q["id"]: q for q in read_json(gold_path)["questions"]}
    missing_gold = [i for i in split_ids if i not in gold_by_id]
    if missing_gold:
        raise ValueError(
            f"No Gold record for {missing_gold}; run build_gtsqa_gold.py first."
        )

    existing = read_output_ids(output_path)
    extra = [i for i in existing if i not in set(split_ids)]
    if extra:
        raise ValueError(f"{output_path.name} holds IDs outside the split: {extra}")

    to_extract = [i for i in split_ids if i not in set(existing)]
    print(f"{output_path.name}: {len(existing)} present, "
          f"{len(to_extract)} to extract")

    if to_extract and not args.verify_only:
        if not ends_with_newline(output_path):
            raise ValueError(f"{output_path.name} does not end with a newline.")
        extract(to_extract, output_path)

    print("\nVerifying graphs against Gold ...")
    if not verify(split_ids, output_path, gold_by_id):
        sys.exit(1)


if __name__ == "__main__":
    main()
