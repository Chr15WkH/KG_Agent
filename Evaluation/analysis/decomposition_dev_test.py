"""
Request decomposition test on the GTSQA development split.

Runs the real ARK v2 graph and stops right after decompose_request for every question, then saves
the known entity table, the constraints and the answer type to logs/decomposition_dev_<tag>.json.
Each tag in TAGS is one pass over all questions. Questions already in an output file are skipped,
so an interrupted pass continues where it stopped when the script is run again.
The first pass prints each result next to the gold SPARQL query; later passes print one line per question.

Usage (from the project root):
    python -u -B Evaluation/analysis/decomposition_dev_test.py

Results used in the thesis: results/dev/decomposition_dev_v3.json and results/dev/decomposition_dev_v3b.json
(two passes with the same prompt).
"""

import gc
import json
import logging
import time
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(dotenv_path=PROJECT_ROOT / ".env", override=True)

from ark_v2.ark_v2 import ARK_V2
from ark_v2.adapters.gtsqa import adapt_gtsqa_sample
from ark_v2.data_models.agent_models import QuestionTypes

MODEL = "qwen3.8:27b"
TAGS = ("v3", "v3b")  # one pass per tag, each saved to its own file
INPUT = PROJECT_ROOT / "Dataset" / "gtsqa_development_agent_input.jsonl"
GOLD = PROJECT_ROOT / "Dataset" / "gtsqa_development_gold.json"
OUTPUT_DIR = PROJECT_ROOT / "logs"

logging.basicConfig(level=logging.WARNING)

CONFIG = {
    "complete_answer_qids": True,
    "known_entities_hint": True,
    "request_decomposition": True,
    "llm": {"model": MODEL, "temperature": 0.9, "top_p": 0.9, "seed": 42},
}


def as_dict(value):
    """Return a pydantic model as a dict; other values unchanged."""
    return value.model_dump() if hasattr(value, "model_dump") else value


def exploration_of(update):
    """Exploration record (dict) from one node update; None if the update has none."""
    update = as_dict(update) or {}
    return as_dict(update.get("exploration"))


gold_sparql = {}
for q in json.loads(GOLD.read_text(encoding="utf-8"))["questions"]:
    gold_sparql[q["id"]] = q["generation_reference"]["sparql_query"]

OUTPUT_DIR.mkdir(exist_ok=True)

for tag in TAGS:
    output = OUTPUT_DIR / f"decomposition_dev_{tag}.json"
    results = json.loads(output.read_text(encoding="utf-8")) if output.exists() else []
    done = {r["id"] for r in results}
    verbose = tag == TAGS[0]
    print(f"\n######## pass {tag} -> {output}")

    with INPUT.open(encoding="utf-8") as file:
        for line in file:
            raw = json.loads(line)
            if raw["id"] in done:
                continue
            start = time.time()
            sample = adapt_gtsqa_sample(raw)

            agent = ARK_V2()
            agent.load_configuration(config=CONFIG)
            agent.load_graph_data(sample["graph"])
            agent.set_initial_state(question=sample["question"], question_type=QuestionTypes.ENTITY_LIST)

            # Run the real graph and stop right after decompose_request
            extracted, decomposed = None, None
            for chunk in agent.graph.stream(
                agent.initial_state, stream_mode="updates", config={"recursion_limit": 200}
            ):
                if "extract_known_entities" in chunk:
                    extracted = exploration_of(chunk["extract_known_entities"])
                if "decompose_request" in chunk:
                    decomposed = exploration_of(chunk["decompose_request"])
                    break
            if decomposed is None:
                print(f"WARNING {raw['id']}: no exploration record after decompose_request")
                decomposed = extracted or {}

            n_extracted = len((extracted or {}).get("known_entities", []))
            record = {
                "id": raw["id"],
                "question": sample["question"],
                "n_extracted": n_extracted,
                "known_entities": decomposed.get("known_entities", []),
                "constraints": decomposed.get("constraints", []),
                "answer_type": decomposed.get("answer_type"),
                "seconds": round(time.time() - start, 1),
            }
            results.append(record)
            output.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

            print(f"\n[{len(results)}/38] {raw['id']}  ({record['seconds']} s)")
            if verbose:
                print(f"  Q: {sample['question']}")
                for i, e in enumerate(record["known_entities"]):
                    # '*' marks an entity added by decompose_request, not by extraction
                    mark = "*" if i >= n_extracted else " "
                    print(f"  {e['id']}{mark} {e['mention']} -> {', '.join(e['entities']) or 'not found'}")
                for c in record["constraints"]:
                    print(f"  {c['id']}: {c['subject']} - {c['relation']} - {c['object']}")
                print(f"  answer_type: {record['answer_type']}")
                print(f"  gold: {gold_sparql.get(raw['id'])}")

            del agent
            gc.collect()

    print(f"\npass {tag}: {len(results)}/38 questions done, saved to {output}")
