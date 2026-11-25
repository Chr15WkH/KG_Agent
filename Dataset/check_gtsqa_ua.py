"""Check a GTSQA_UA Gold file for deleted facts that remain recoverable.

For each unanswerable variant, the graph is rebuilt from the GTSQA agent
input by removing the recorded edges. A variant is flagged when

- a recorded edge is absent from the source graph,
- the Gold SPARQL query still returns answers, or
- any edge remains between the two endpoints of a deleted fact. Such an edge
  is a symmetric or inverse statement of the deleted fact, or another fact
  about the same two entities; a person decides which.

Files from the first version of build_gtsqa_ua.py, which have no
"removed_facts", are checked with their removed_triples as the facts.

Read-only: nothing is written.

Run from the project root:
    python Dataset/check_gtsqa_ua.py Dataset/gtsqa_ua_test_gold.json
    python Dataset/check_gtsqa_ua.py Dataset/gtsqa_ua_test_gold.json --verbose
    python Dataset/check_gtsqa_ua.py <gold file> --input <agent input jsonl>

With --verbose, every variant lists its deleted facts and the edges removed
with them, not only the flagged ones.

The agent input defaults to the file named in the Gold file's dataset_info.
Exits with status 1 if any variant is flagged.

Requires:
    rdflib
"""

import argparse
import json
import re
import sys
from pathlib import Path

from build_gtsqa_ua import (
    DATASET_DIR,
    endpoint_edges,
    execute_query,
    make_graph,
    normalize_triple,
    read_json,
)


LABELLED = re.compile(r"(.+) \(([QP][1-9][0-9]*)\)")


def load_graphs(input_path, source_ids):
    """Stream the agent input once, keeping only the requested graphs."""
    graphs = {}

    with input_path.open("r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue

            sample = json.loads(line)
            sample_id = str(sample["id"])
            if sample_id not in source_ids:
                continue

            if sample_id in graphs:
                raise ValueError(f"Duplicate source sample: {sample_id}.")
            graphs[sample_id] = sample["graph"]

    missing = sorted(source_ids - graphs.keys())
    if missing:
        raise ValueError(f"Source samples not found: {missing}.")

    return graphs


def labels_of(raw_graph):
    labels = {}
    for triple in raw_graph:
        for value in triple:
            match = LABELLED.fullmatch(value.strip())
            if match:
                labels[match.group(2)] = match.group(1)
    return labels


def show(triple, labels):
    head, relation, tail = triple
    return (
        f"{labels.get(head, '?')} ({head}) "
        f"—[{labels.get(relation, '?')} ({relation})]→ "
        f"{labels.get(tail, '?')} ({tail})"
    )


def check_file(gold_path, input_path, verbose=False):
    data = read_json(gold_path)
    variants = [
        record
        for record in data["questions"]
        if record["modification"]["type"] == "fact_deletion"
    ]
    source_of = {
        record["id"]: record["id"].split("-", 1)[0] for record in variants
    }
    graphs = load_graphs(input_path, set(source_of.values()))

    flagged = 0

    for record in variants:
        raw_graph = graphs[source_of[record["id"]]]
        triples = {normalize_triple(triple) for triple in raw_graph}

        modification = record["modification"]
        removed = {
            normalize_triple(triple)
            for triple in modification["removed_triples"]
        }
        facts = [
            normalize_triple(triple)
            for triple in modification.get(
                "removed_facts", modification["removed_triples"]
            )
        ]

        problems = []
        if not removed <= triples:
            problems.append(
                f"recorded edges absent from the graph: "
                f"{sorted(removed - triples)}"
            )

        modified = triples - removed
        answers = execute_query(make_graph(modified), record["sparql_query"])
        if answers:
            problems.append(f"query still returns {answers}")

        remaining = endpoint_edges(modified, facts)

        ok = not problems and not remaining
        print(f"{record['id']}: {'ok' if ok else 'FLAGGED'}")
        if ok and not verbose:
            continue

        flagged += 0 if ok else 1
        labels = labels_of(raw_graph)
        for fact in facts:
            print(f"    deleted fact: {show(fact, labels)}")
        for edge in sorted(removed - set(facts)):
            print(f"    also removed: {show(edge, labels)}")
        for edge in remaining:
            print(f"    remains     : {show(edge, labels)}")
        for problem in problems:
            print(f"    problem     : {problem}")

    print(f"\n{len(variants)} variant(s) checked, {flagged} flagged.")
    return flagged


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("gold", type=Path, help="GTSQA_UA Gold file")
    parser.add_argument("--input", type=Path, help="GTSQA agent input jsonl")
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="List deleted facts and removed edges for every variant.",
    )
    args = parser.parse_args()

    input_path = args.input
    if input_path is None:
        source = read_json(args.gold)["dataset_info"]["source_agent_input"]
        input_path = DATASET_DIR / source

    flagged = check_file(args.gold, input_path, args.verbose)
    sys.exit(1 if flagged else 0)


if __name__ == "__main__":
    main()
