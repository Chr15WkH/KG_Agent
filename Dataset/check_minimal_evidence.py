"""Check that every Gold evidence triple is necessary.

A question is kept only if removing any single triple from its Gold
evidence (full_answer_subgraph_wikikg2) makes its SPARQL query return
no answer. As a validity precondition, the query on the complete Gold
evidence must return the Gold answers.

Run from the project root:
    python Dataset/check_minimal_evidence.py
    python Dataset/check_minimal_evidence.py --gold Dataset/<other_gold>.json
    python Dataset/check_minimal_evidence.py --report Dataset/<new_report>.json

Requires:
    rdflib

Read-only by default. --report writes a new file and never overwrites.
"""

import argparse
import json
import re
from pathlib import Path

from build_gtsqa_ua import (
    DATASET_DIR,
    execute_query,
    make_graph,
    normalize_answers,
    normalize_triple,
    rdf_triple,
)


DEFAULT_GOLD = DATASET_DIR / "gtsqa_development_gold.json"

# With these constructs, removing facts can add answers, so the
# single-deletion test no longer proves minimality.
NON_MONOTONE = re.compile(
    r"\b(OPTIONAL|MINUS|NOT\s+EXISTS|FILTER|GROUP\s+BY|HAVING|COUNT)\b",
    re.IGNORECASE,
)


def load_questions(path):
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    questions = data["questions"]
    ids = [str(question["id"]) for question in questions]
    if len(ids) != len(set(ids)):
        raise ValueError("Gold file contains duplicate question IDs.")

    return questions


def is_monotone(query):
    return NON_MONOTONE.search(query) is None


def check_question(question):
    """Return a result dictionary; data or query errors propagate."""
    query = question["generation_reference"]["sparql_query"]
    gold = question["evaluation_gold"]

    evidence = sorted({
        normalize_triple(triple)
        for triple in gold["full_answer_subgraph_wikikg2"]
    })
    expected = normalize_answers(gold["all_answers_wikikg2"])

    result = {
        "id": str(question["id"]),
        "status": None,
        "n_triples": len(evidence),
        "reason": "",
        "removable_triples": [],
    }

    if not evidence:
        raise ValueError("Gold evidence is empty.")
    if not expected:
        raise ValueError("Gold answer is empty.")

    if not is_monotone(query):
        result["status"] = "MANUAL"
        result["reason"] = "query is not monotone; check by hand"
        return result

    graph = make_graph(evidence)

    # Precondition: the complete Gold evidence answers the question.
    found = execute_query(graph, query)
    if found != expected:
        raise ValueError(
            f"Query on Gold evidence returns {found}, Gold is {expected}."
        )

    # Core check: no single triple can be removed.
    removable = []
    for triple in evidence:
        graph.remove(rdf_triple(triple))
        try:
            if execute_query(graph, query):
                removable.append(list(triple))
        finally:
            graph.add(rdf_triple(triple))

    if removable:
        result["status"] = "FAIL"
        result["reason"] = (
            f"{len(removable)} triple(s) can be removed "
            "and the query still returns an answer"
        )
        result["removable_triples"] = removable
    else:
        result["status"] = "PASS"

    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--gold", type=Path, default=DEFAULT_GOLD)
    parser.add_argument("--report", type=Path, default=None)
    args = parser.parse_args()

    questions = load_questions(args.gold)
    results = []

    for question in questions:
        try:
            result = check_question(question)
        except Exception as error:
            # Errors are never counted as passed.
            result = {
                "id": str(question.get("id")),
                "status": "ERROR",
                "n_triples": None,
                "reason": f"{type(error).__name__}: {error}",
                "removable_triples": [],
            }

        results.append(result)

        size = (
            f"{result['n_triples']} triples"
            if result["n_triples"] is not None else ""
        )
        print(f"{result['id']:<8} {result['status']:<7} {size:<11} "
              f"{result['reason']}")
        for triple in result["removable_triples"]:
            print(f"{'':<8} removable: ({', '.join(triple)})")

    counts = {
        status: sum(r["status"] == status for r in results)
        for status in ("PASS", "FAIL", "MANUAL", "ERROR")
    }
    print(
        f"\n{len(results)} checked, {counts['PASS']} kept "
        f"(FAIL {counts['FAIL']} · MANUAL {counts['MANUAL']} · "
        f"ERROR {counts['ERROR']})"
    )

    if args.report is not None:
        report = {
            "source_gold": str(args.gold),
            "criterion": (
                "Removing any single triple from "
                "full_answer_subgraph_wikikg2 makes the SPARQL query "
                "return no answer."
            ),
            "summary": {"checked": len(results), **counts},
            "results": results,
        }
        with args.report.open("x", encoding="utf-8") as file:
            json.dump(report, file, ensure_ascii=False, indent=2)
            file.write("\n")
        print(f"Report saved to {args.report}")


if __name__ == "__main__":
    main()
