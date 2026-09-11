import json
from collections import defaultdict
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
INPUT_PATH = (
    PROJECT_ROOT
    / "Dataset"
    / "gtsqa_development_agent_input.jsonl"
)
SAMPLE_ID = 13311


def load_sample(sample_id):
    """Read one sample without keeping all graphs in memory."""
    with INPUT_PATH.open("r", encoding="utf-8") as file:
        for line in file:
            sample = json.loads(line)
            if sample["id"] == sample_id:
                return sample

    raise ValueError(f"Sample {sample_id} was not found.")


def main():
    sample = load_sample(SAMPLE_ID)

    nodes = set()
    relations_by_head = defaultdict(set)
    triples_by_query = defaultdict(list)

    for head, relation, tail in sample["graph"]:
        nodes.update((head, tail))
        relations_by_head[head].add(relation)
        triples_by_query[(head, relation)].append(
            (head, relation, tail)
        )

    print(f"Sample: {sample['id']}")
    print(f"Question: {sample['question']}")
    print(f"Nodes: {len(nodes)}")
    print(f"Input triples: {len(sample['graph'])}")

    print("\nTop 5 anchors by outgoing relation count:")

    ranked_heads = sorted(
        relations_by_head,
        key=lambda head: (-len(relations_by_head[head]), head),
    )

    for head in ranked_heads[:5]:
        relations = sorted(relations_by_head[head])
        prompt_text = (
            f"Relations connected to entity {head}: {relations}"
        )

        print(
            f"  {head}\n"
            f"    relations={len(relations)}, "
            f"relation_message_chars={len(prompt_text)}"
        )

    print("\nTop 5 queries by returned triple count:")

    ranked_queries = sorted(
        triples_by_query,
        key=lambda query: (-len(triples_by_query[query]), query),
    )

    for query in ranked_queries[:5]:
        head, relation = query
        triples = triples_by_query[query]

        # Approximate ARK's current triple message representation.
        # "xxxx" stands in for its four-character triple key.
        displayed_triples = [
            {"xxxx": (h, t, {"relation": r})}
            for h, r, t in triples
        ]
        prompt_text = "Retrieved Triples: \n" + str(displayed_triples)

        print(
            f"  anchor: {head}\n"
            f"  relation: {relation}\n"
            f"    triples={len(triples)}, "
            f"approx_triple_message_chars={len(prompt_text)}"
        )


if __name__ == "__main__":
    main()