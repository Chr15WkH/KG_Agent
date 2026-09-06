import json
from collections import defaultdict
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATASET_PATH = (
    PROJECT_ROOT
    / "Dataset"
    / "gtsqa_development_agent_input.jsonl"
)


def analyze_sample(sample):
    relations_by_node_pair = defaultdict(set)

    for triple in sample["graph"]:
        head, relation, tail = triple
        relations_by_node_pair[(head, tail)].add(relation)

    multi_relation_pairs = {
        node_pair: relations
        for node_pair, relations in relations_by_node_pair.items()
        if len(relations) > 1
    }

    overwritten_relations = sum(
        len(relations) - 1
        for relations in multi_relation_pairs.values()
    )

    return multi_relation_pairs, overwritten_relations


def main():
    total_samples = 0
    affected_samples = 0
    total_multi_relation_pairs = 0
    total_overwritten_relations = 0

    with DATASET_PATH.open("r", encoding="utf-8") as file:
        for line in file:
            sample = json.loads(line)
            total_samples += 1

            multi_relation_pairs, overwritten_relations = analyze_sample(
                sample
            )

            pair_count = len(multi_relation_pairs)

            if pair_count > 0:
                affected_samples += 1

            total_multi_relation_pairs += pair_count
            total_overwritten_relations += overwritten_relations

            print(
                f"Sample {sample['id']}: "
                f"graph triples={len(sample['graph'])}, "
                f"multi-relation pairs={pair_count}, "
                f"relations lost by DiGraph={overwritten_relations}"
            )

            for pair_index, (node_pair, relations) in enumerate(
                multi_relation_pairs.items()
            ):
                if pair_index >= 3:
                    break

                head, tail = node_pair

                print(f"  head: {head}")
                print(f"  tail: {tail}")
                print(f"  relations: {sorted(relations)}")

    print()
    print("Summary")
    print(f"Samples checked: {total_samples}")
    print(f"Affected samples: {affected_samples}")
    print(
        "Multi-relation node pairs: "
        f"{total_multi_relation_pairs}"
    )
    print(
        "Relations that DiGraph would lose: "
        f"{total_overwritten_relations}"
    )


if __name__ == "__main__":
    main()