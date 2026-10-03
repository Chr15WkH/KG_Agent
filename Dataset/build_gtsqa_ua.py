"""Build a small GTSQA_UA development Gold dataset.

Run from the project root:
    python Dataset/build_gtsqa_ua.py

Requires:
    rdflib

Original files are read-only. Existing output is not overwritten.
"""

import argparse
import json
import re
from itertools import combinations
from pathlib import Path

from rdflib import Graph, Namespace, URIRef


DATASET_DIR = Path(__file__).resolve().parent
INPUT_PATH = DATASET_DIR / "gtsqa_development_agent_input.jsonl"
GOLD_PATH = DATASET_DIR / "gtsqa_development_gold.json"
OUTPUT_PATH = DATASET_DIR / "gtsqa_ua_gold.json"

WD = Namespace("http://www.wikidata.org/entity/")
WDT = Namespace("http://www.wikidata.org/prop/direct/")

PREFIXES = (
    "PREFIX wd: <http://www.wikidata.org/entity/>\n"
    "PREFIX wdt: <http://www.wikidata.org/prop/direct/>\n"
)

# Bound candidate enumeration if larger samples are added later.
MAX_CANDIDATE_FACTS = 8


def read_json(path):
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def extract_id(value, prefix):
    """Accept a QID/PID or 'label (QID/PID)'."""
    if not isinstance(value, str):
        raise ValueError(f"Expected a string, received {value!r}.")

    value = value.strip()
    pattern = rf"{prefix}[1-9][0-9]*"

    if re.fullmatch(pattern, value):
        return value

    match = re.fullmatch(rf".+\(({pattern})\)", value)
    if match:
        return match.group(1)

    raise ValueError(f"Invalid {prefix} identifier: {value!r}.")


def normalize_triple(triple):
    """Return canonical [head, relation, tail] identifiers."""
    if not isinstance(triple, (list, tuple)) or len(triple) != 3:
        raise ValueError(f"Invalid triple: {triple!r}.")

    head, relation, tail = triple
    return (
        extract_id(head, "Q"),
        extract_id(relation, "P"),
        extract_id(tail, "Q"),
    )


def normalize_answers(answers):
    if not isinstance(answers, list):
        raise ValueError("Answers must be a list.")

    return sorted({extract_id(answer, "Q") for answer in answers})


def rdf_triple(triple):
    head, relation, tail = triple
    return WD[head], WDT[relation], WD[tail]


def make_graph(triples):
    graph = Graph()
    for triple in triples:
        graph.add(rdf_triple(triple))
    return graph


def execute_query(graph, query):
    """Execute the current dataset's local SELECT ?answer queries.

    Query errors propagate; they are never converted to empty results.
    """
    if not isinstance(query, str):
        raise ValueError("SPARQL query must be a string.")

    if not re.match(r"^\s*SELECT\b", query, re.IGNORECASE):
        raise ValueError("Expected SELECT without explicit PREFIX clauses.")

    # No remote queries or truncated results in dataset validation.
    if re.search(
        r"\b(SERVICE|FROM|LIMIT|OFFSET)\b",
        query,
        re.IGNORECASE,
    ):
        raise ValueError("SERVICE, FROM, LIMIT and OFFSET are unsupported.")

    result = graph.query(PREFIXES + query)

    if result.type != "SELECT":
        raise ValueError("Expected a SELECT result.")

    if [str(variable) for variable in result.vars] != ["answer"]:
        raise ValueError("The query must select only ?answer.")

    answers = set()
    namespace = str(WD)

    for row in result:
        value = row[0]
        if (
            not isinstance(value, URIRef)
            or not str(value).startswith(namespace)
        ):
            raise ValueError(f"Expected an entity answer, received {value!r}.")

        answers.add(extract_id(str(value)[len(namespace):], "Q"))

    return sorted(answers)


def load_source_sample(sample_id):
    """Stream the source file, retaining one sample graph."""
    match = None

    with INPUT_PATH.open("r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue

            sample = json.loads(line)
            if str(sample["id"]) != str(sample_id):
                continue

            if match is not None:
                raise ValueError(f"Duplicate source sample: {sample_id}.")
            match = sample

    if match is None:
        raise ValueError(f"Source sample {sample_id} was not found.")

    return match


def find_deletion(graph, evidence, query, max_delete):
    """Try single facts first, then pairs; return the first valid deletion."""
    candidates = sorted(set(evidence))

    if not candidates:
        raise ValueError("Gold evidence is empty.")

    if len(candidates) > MAX_CANDIDATE_FACTS:
        raise ValueError(
            f"{len(candidates)} candidate facts exceed the limit "
            f"of {MAX_CANDIDATE_FACTS}."
        )

    for count in range(1, min(max_delete, len(candidates)) + 1):
        for removed in combinations(candidates, count):
            try:
                for triple in removed:
                    graph.remove(rdf_triple(triple))

                if not execute_query(graph, query):
                    return list(removed)

            finally:
                for triple in removed:
                    graph.add(rdf_triple(triple))

    return None


def make_record(
    sample,
    suffix,
    original_answers,
    removed,
    query,
    modified_answers,
):
    """Dictionary insertion order defines the saved field order."""
    answerable = bool(modified_answers)

    return {
        "id": f"{sample['id']}-{suffix}",
        "question": sample["question"],
        "answerable": answerable,
        "gold_answer": modified_answers if answerable else None,
        "original_gold_answer": original_answers,
        "modification": {
            "type": "fact_deletion" if removed else "none",
            "removed_triples": [list(triple) for triple in removed],
        },
        "sparql_query": query,
        "validation": {
            "status": "passed",
            "original_query_answers": original_answers,
            "deletion_matches_record": True,
            "modified_query_answers": modified_answers,
            "error": None,
        },
    }


def build_pair(gold, max_delete):
    """Return one verified original/UA pair."""
    sample = load_source_sample(gold["id"])

    question = gold["question_profile"]["question"]
    if not isinstance(question, str) or not question.strip():
        raise ValueError("Question is empty or invalid.")
    if sample["question"] != question:
        raise ValueError("Input question differs from Gold.")

    raw_graph = sample.get("graph")
    if not isinstance(raw_graph, list) or not raw_graph:
        raise ValueError("Original graph is empty or invalid.")

    triples = {normalize_triple(triple) for triple in raw_graph}
    expected = normalize_answers(
        gold["evaluation_gold"]["all_answers_wikikg2"]
    )

    if not expected:
        raise ValueError("Original sample must have a non-empty Gold answer.")

    query = gold["generation_reference"]["sparql_query"]
    graph = make_graph(triples)
    original_answers = execute_query(graph, query)

    if original_answers != expected:
        raise ValueError(
            f"Original query/Gold mismatch: "
            f"query={original_answers}, gold={expected}."
        )

    evidence = {
        normalize_triple(triple)
        for triple in gold["evaluation_gold"][
            "full_answer_subgraph_wikikg2"
        ]
    }

    if not evidence.issubset(triples):
        raise ValueError("Some Gold evidence facts are absent from the graph.")

    removed = find_deletion(graph, evidence, query, max_delete)
    if removed is None:
        raise ValueError("No valid deletion found within the configured limit.")

    removed_set = set(removed)

    # Reconstruct from the original labeled graph for an independent
    # check of the actual deletion operation.
    modified_raw = [
        triple
        for triple in raw_graph
        if normalize_triple(triple) not in removed_set
    ]
    modified_triples = {
        normalize_triple(triple) for triple in modified_raw
    }

    if modified_triples != triples - removed_set:
        raise ValueError("Actual graph changes differ from the deletion record.")

    modified_answers = execute_query(make_graph(modified_triples), query)
    if modified_answers:
        raise ValueError("Reconstructed UA graph still returns answers.")

    return [
        make_record(
            sample,
            "original",
            original_answers,
            [],
            query,
            original_answers,
        ),
        make_record(
            sample,
            "ua-01",
            original_answers,
            removed,
            query,
            modified_answers,
        ),
    ]


def build_dataset(output_path, max_delete):
    if output_path.exists():
        raise FileExistsError(
            f"Output already exists: {output_path}. "
            "Use --output with a new filename."
        )

    source_gold = read_json(GOLD_PATH)
    questions = source_gold["questions"]

    ids = [str(item["id"]) for item in questions]
    if len(ids) != len(set(ids)):
        raise ValueError("Original Gold contains duplicate IDs.")

    records = []
    skipped = []

    for gold in questions:
        try:
            pair = build_pair(gold, max_delete)
        except Exception as error:
            # Failed queries or invalid source data never become UA labels.
            skipped.append({
                "id": str(gold["id"]),
                "status": "needs_review",
                "error": f"{type(error).__name__}: {error}",
            })
            print(f"{gold['id']}: skipped — {error}")
            continue

        records.extend(pair)
        removed_count = len(pair[1]["modification"]["removed_triples"])
        print(f"{gold['id']}: passed — deleted {removed_count} fact(s)")

    dataset = {
        "dataset_info": {
            "name": "gtsqa_ua_development",
            "source_agent_input": INPUT_PATH.name,
            "source_gold": GOLD_PATH.name,
            "construction_method": "controlled_fact_deletion",
            "candidate_order": "sorted_qid_pid_triples",
            "max_deleted_facts": max_delete,
            "pair_count": len(records) // 2,
            "item_count": len(records),
            "answerability_definition": (
                "The original query returns verified non-empty answers. "
                "A deleted variant is unanswerable when the same query "
                "executes successfully and returns no answers."
            ),
        },
        "questions": records,
        "skipped": skipped,
    }

    with output_path.open("x", encoding="utf-8") as file:
        json.dump(dataset, file, ensure_ascii=False, indent=2)
        file.write("\n")

    print(
        f"Saved {len(records) // 2} pairs to {output_path}; "
        f"skipped {len(skipped)} source item(s)."
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    parser.add_argument("--max-delete", type=int, choices=(1, 2), default=2)
    args = parser.parse_args()

    build_dataset(args.output, args.max_delete)


if __name__ == "__main__":
    main()