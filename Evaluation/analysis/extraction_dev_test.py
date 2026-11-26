"""
Known entity extraction test on the GTSQA development split.

Runs the real ARK v2 graph and stops right after extract_known_entities, RUNS times per question,
then compares the extracted entities with the gold seed entities. No exploration step runs.
Run 1 prints the full result (entities, common neighbours, hint); later runs print one line.

Usage (from the project root; the output is also saved to a text file):
    python -u -B Evaluation/analysis/extraction_dev_test.py 2>&1 | tee logs/extraction_dev_after.txt

Results used in the thesis: results/dev/extraction_dev_before.txt and results/dev/extraction_dev_after.txt
(before and after verifying known entities by name in the whole graph).
"""

import os
os.environ["TQDM_DISABLE"] = "1"  # hide embedding progress bars
import json
import logging
import time
import warnings
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(dotenv_path=PROJECT_ROOT / ".env", override=True)
logging.basicConfig(level=logging.WARNING)
warnings.filterwarnings("ignore", message="Pydantic serializer warnings")

from ark_v2.ark_v2 import ARK_V2, _render_known_entities_hint
from ark_v2.data_models.agent_models import QuestionTypes, RuntimeState
from ark_v2.adapters.gtsqa import adapt_gtsqa_sample

RUNS = 3  # extraction runs per question

root = PROJECT_ROOT / "Dataset"
gold = {}
for q in json.loads((root / "gtsqa_development_gold.json").read_text(encoding="utf-8"))["questions"]:
    path_entities = set()
    for head, relation, tail in q["generation_reference"]["answer_subgraph"]:
        path_entities.add(head)
        path_entities.add(tail)
    gold[q["id"]] = {"seeds": q["entity_linking_gold"]["seed_entities"], "path": path_entities}

config = {
    "complete_answer_qids": True,
    "known_entities_hint": True,
    "llm": {"model": "qwen3.8:27b", "temperature": 0.9, "top_p": 0.9, "seed": 42},
}
agent = ARK_V2()
agent.load_configuration(config=config)
print(f"Extraction temperature: {agent.extraction_llm.temperature} (other steps: {agent.llm.temperature})")


def label(entity, info):
    if entity in info["seeds"]:
        return "[gold seed]"
    if entity in info["path"]:
        return "[gold path]"
    return "[not gold]"


def extract(initial_state):
    """Run the real graph and stop right after the extraction node; return the state."""
    for event in agent.graph.stream(initial_state, stream_mode="updates"):
        if "extract_known_entities" in event:
            value = event["extract_known_entities"]
            return value if isinstance(value, RuntimeState) else RuntimeState.model_validate(value)
    return None


summary = []
with (root / "gtsqa_development_agent_input.jsonl").open(encoding="utf-8") as file:
    for line in file:
        raw = json.loads(line)
        if raw["id"] not in gold:
            continue
        info = gold[raw["id"]]
        sample = adapt_gtsqa_sample(raw)
        agent.load_graph_data(sample["graph"])
        agent.set_initial_state(question=sample["question"], question_type=QuestionTypes.ENTITY_LIST)

        print(f"\n==== {raw['id']}")
        print(f"Q: {sample['question']}")
        print(f"Gold seeds: {'; '.join(info['seeds'])}")

        hits_per_run = []
        extra_per_run = []
        for run in range(1, RUNS + 1):
            start = time.time()
            state = extract(agent.initial_state.model_copy(deep=True))
            seconds = time.time() - start

            found = []
            mentions = []
            for record in state.exploration.known_entities:
                mentions.append(record["mention"])
                for entity in record["entities"]:
                    found.append(entity)
            missed = []
            for seed in info["seeds"]:
                if seed not in found:
                    missed.append(seed)
            extra = []
            for entity in found:
                if entity not in info["seeds"]:
                    extra.append(entity)
            hits_per_run.append(len(info["seeds"]) - len(missed))
            extra_per_run.append(len(extra))

            if run > 1:
                print(f"run {run} ({seconds:.1f} s): mentions {mentions}; "
                      f"missed: {'; '.join(missed) or 'none'}; extra: {'; '.join(extra) or 'none'}")
                continue

            print(f"run 1 ({seconds:.1f} s)")
            print("Extracted:")
            for record in state.exploration.known_entities:
                if not record["entities"]:
                    print(f"  {record['id']} \"{record['mention']}\" -> not found")
                    continue
                for entity in record["entities"]:
                    print(f"  {record['id']} \"{record['mention']}\" -> {entity}  {label(entity, info)}")
            if not state.exploration.known_entities:
                print("  none")
            print(f"Missed gold seeds: {'; '.join(missed) or 'none'}")

            print("Common neighbors:")
            for pair in state.exploration.common_neighbors:
                neighbors = pair["neighbors"]
                on_path = []
                for entity in neighbors:
                    if entity in info["path"]:
                        on_path.append(entity)
                shown = []
                for entity in neighbors[:10]:
                    mark = " [gold path]" if entity in info["path"] else ""
                    shown.append(entity + mark)
                more = f"; and {len(neighbors) - 10} more" if len(neighbors) > 10 else ""
                print(f"  {pair['entity_a']} x {pair['entity_b']}: {len(neighbors)}"
                      + (f" -> {'; '.join(shown)}{more}" if neighbors else ""))
                if len(neighbors) > 10 and on_path:
                    print(f"    gold path entities among all {len(neighbors)}: {'; '.join(on_path)}")
            if not state.exploration.common_neighbors:
                print("  no pairs")

            hint = _render_known_entities_hint(state, agent.max_common_neighbors)
            print("Hint shown in Step 2.1:")
            for hint_line in (hint.strip().splitlines() or ["(empty)"]):
                print(f"  {hint_line}")

        summary.append((raw["id"], len(info["seeds"]), hits_per_run, extra_per_run))

print("\n==== Summary (gold seeds found per run / extra entities per run)")
for sample_id, total, hits, extras in summary:
    print(f"{sample_id:>6}: seeds {total}, found {hits}, extra {extras}")
