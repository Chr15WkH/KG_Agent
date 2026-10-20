"""Load, reconstruct and validate GTSQA_UA samples for ARK_V1_1.

This module does not import the dataset builder or Evaluation.

Requires:
    rdflib
"""

import json
import re
from pathlib import Path

from rdflib import Graph, Namespace, URIRef

from .gtsqa import adapt_gtsqa_sample


# File location:
# KG_Agent/agent/ark_v1_1/ark_v1_1/adapters/gtsqa_ua.py
PROJECT_ROOT = Path(__file__).resolve().parents[4]
DATASET_DIR = PROJECT_ROOT / "Dataset"

DEFAULT_GOLD_PATH = DATASET_DIR / "gtsqa_ua_gold.json"
DEFAULT_INPUT_PATH = DATASET_DIR / "gtsqa_development_agent_input.jsonl"

WD = Namespace("http://www.wikidata.org/entity/")
WDT = Namespace("http://www.wikidata.org/prop/direct/")

PREFIXES = (
    "PREFIX wd: <http://www.wikidata.org/entity/>\n"
    "PREFIX wdt: <http://www.wikidata.org/prop/direct/>\n"
)

VARIANT_PATTERN = re.compile(
    r"(?P<source>[0-9]+)-(?P<variant>original|ua-[0-9]+)"
)


def _extract_id(value, prefix):
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


def _normalize_triple(triple):
    if not isinstance(triple, (list, tuple)) or len(triple) != 3:
        raise ValueError(f"Invalid triple: {triple!r}.")

    head, relation, tail = triple
    return (
        _extract_id(head, "Q"),
        _extract_id(relation, "P"),
        _extract_id(tail, "Q"),
    )


def _normalize_answers(answers):
    if not isinstance(answers, list):
        raise ValueError("Answers must be a list.")

    return sorted({_extract_id(answer, "Q") for answer in answers})


def _make_graph(triples):
    graph = Graph()
    for head, relation, tail in triples:
        graph.add((WD[head], WDT[relation], WD[tail]))
    return graph


def _execute_query(graph, query):
    if not isinstance(query, str):
        raise ValueError("SPARQL query must be a string.")

    if not re.match(r"^\s*SELECT\b", query, re.IGNORECASE):
        raise ValueError("Expected SELECT without explicit PREFIX clauses.")

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

        answers.add(_extract_id(str(value)[len(namespace):], "Q"))

    return sorted(answers)


def _load_gold_record(variant_id, gold_path):
    with Path(gold_path).open("r", encoding="utf-8") as file:
        data = json.load(file)

    matches = [
        item
        for item in data["questions"]
        if item["id"] == variant_id
    ]

    if len(matches) != 1:
        raise ValueError(
            f"Expected one Gold record for {variant_id}, "
            f"found {len(matches)}."
        )

    return matches[0]


def _load_original_sample(source_id, input_path):
    match = None

    with Path(input_path).open("r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue

            sample = json.loads(line)
            if str(sample["id"]) != source_id:
                continue

            if match is not None:
                raise ValueError(f"Duplicate original sample: {source_id}.")
            match = sample

    if match is None:
        raise ValueError(f"Original sample {source_id} was not found.")

    return match


def load_gtsqa_ua_sample(
    variant_id,
    *,
    gold_path=DEFAULT_GOLD_PATH,
    input_path=DEFAULT_INPUT_PATH,
):
    """Return validated {id, question, graph} in GTSQA triple order.

    No Gold answers, answerability labels, queries or deletion metadata
    are included in the returned sample.
    """
    if not isinstance(variant_id, str):
        raise ValueError("Variant ID must be a string.")

    match = VARIANT_PATTERN.fullmatch(variant_id)
    if not match:
        raise ValueError(
            "Expected an ID such as '13311-original' or '13311-ua-01'."
        )

    gold = _load_gold_record(variant_id, gold_path)
    original = _load_original_sample(match.group("source"), input_path)

    if gold["validation"]["status"] != "passed":
        raise ValueError("Gold record has not passed construction validation.")

    if type(gold["answerable"]) is not bool:
        raise ValueError("answerable must be a Boolean.")

    if gold["question"] != original["question"]:
        raise ValueError("UA question differs from the original question.")

    raw_graph = original.get("graph")
    if not isinstance(raw_graph, list) or not raw_graph:
        raise ValueError("Original graph is empty or invalid.")

    original_triples = {
        _normalize_triple(triple) for triple in raw_graph
    }

    # Recheck the source graph/query before interpreting an empty result.
    expected_original = _normalize_answers(gold["original_gold_answer"])
    if not expected_original:
        raise ValueError("Original Gold answer must be non-empty.")

    rdf_graph = _make_graph(original_triples)
    actual_original = _execute_query(rdf_graph, gold["sparql_query"])

    if actual_original != expected_original:
        raise ValueError(
            f"Original query/Gold mismatch: "
            f"query={actual_original}, gold={expected_original}."
        )

    modification = gold["modification"]
    removed_raw = modification["removed_triples"]
    if not isinstance(removed_raw, list):
        raise ValueError("removed_triples must be a list.")

    removed = [_normalize_triple(triple) for triple in removed_raw]
    removed_set = set(removed)

    if len(removed) != len(removed_set):
        raise ValueError("Deletion record contains duplicate facts.")

    if modification["type"] == "none":
        if removed:
            raise ValueError("Modification 'none' cannot contain deletions.")
    elif modification["type"] == "fact_deletion":
        if not removed:
            raise ValueError("Fact deletion requires at least one fact.")
    else:
        raise ValueError(
            f"Unsupported modification: {modification['type']!r}."
        )

    if match.group("variant") == "original":
        if modification["type"] != "none" or not gold["answerable"]:
            raise ValueError("Original control has inconsistent metadata.")

    if not removed_set.issubset(original_triples):
        missing = sorted(removed_set - original_triples)
        raise ValueError(f"Deletion facts are absent from the graph: {missing}")

    # Preserve original labels and GTSQA [head, relation, tail] order.
    prepared_graph = [
        list(triple)
        for triple in raw_graph
        if _normalize_triple(triple) not in removed_set
    ]

    prepared_triples = {
        _normalize_triple(triple) for triple in prepared_graph
    }
    if prepared_triples != original_triples - removed_set:
        raise ValueError("Actual graph changes differ from modification.")

    # Reuse the RDF graph rather than retaining another full RDF graph.
    for head, relation, tail in removed:
        rdf_graph.remove((WD[head], WDT[relation], WD[tail]))

    answers = _execute_query(rdf_graph, gold["sparql_query"])

    if gold["answerable"]:
        expected = _normalize_answers(gold["gold_answer"])
        if not expected or answers != expected:
            raise ValueError(
                f"Answerable variant/Gold mismatch: "
                f"query={answers}, gold={expected}."
            )
    else:
        if gold["gold_answer"] is not None:
            raise ValueError("Unanswerable Gold answer must be null.")
        if answers:
            raise ValueError(
                f"Unanswerable variant still returns answers: {answers}."
            )

    return {
        "id": gold["id"],
        "question": gold["question"],
        "graph": prepared_graph,
    }


def adapt_gtsqa_ua_sample(
    variant_id,
    *,
    gold_path=DEFAULT_GOLD_PATH,
    input_path=DEFAULT_INPUT_PATH,
):
    """Return validated input with ARK_V1_1 [head, tail, relation] triples."""
    sample = load_gtsqa_ua_sample(
        variant_id,
        gold_path=gold_path,
        input_path=input_path,
    )
    return adapt_gtsqa_sample(sample)