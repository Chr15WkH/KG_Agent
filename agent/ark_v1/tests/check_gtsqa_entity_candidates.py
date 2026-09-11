import json
from pathlib import Path

from ark_v1.adapters.gtsqa import adapt_gtsqa_sample
from ark_v1.graph.graph_interface import GraphInterface


PROJECT_ROOT = Path(__file__).resolve().parents[3]
INPUT_PATH = (
    PROJECT_ROOT
    / "Dataset"
    / "gtsqa_development_agent_input.jsonl"
)


def main():
    with INPUT_PATH.open("r", encoding="utf-8") as file:
        for line in file:
            sample = json.loads(line)
            if sample["id"] == 13311:
                break
        else:
            raise ValueError("Sample 13311 was not found.")

    sample = adapt_gtsqa_sample(sample)

    interface = GraphInterface()
    interface.load_graph_data(sample["graph"])
    graph = interface.graph

    graph.vectorize()

    # Check that each indexed vector has a corresponding node label.
    assert len(graph.indexed_nodes) == graph.node_index.ntotal

    query = "Silicon Graphics"
    candidates = graph.get_close_nodes(query, k=5)

    print(f"\nQuery: {query}")
    print(f"Indexed nodes: {len(graph.indexed_nodes)}")

    for rank, candidate in enumerate(candidates, start=1):
        print(
            f"{rank}. {candidate['node']} "
            f"score={candidate['distance']:.6f}"
        )

    target = "Silicon Graphics (Q623459)"
    print(f"\nTarget in graph: {target in graph.graph}")
    print(f"Target in index: {target in graph.indexed_nodes}")
    print(
        "Target in top 5: "
        f"{any(item['node'] == target for item in candidates)}"
    )


if __name__ == "__main__":
    main()