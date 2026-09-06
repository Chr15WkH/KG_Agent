import json
import unittest
from pathlib import Path

from ark_v1.adapters.gtsqa import (
    adapt_gtsqa_sample,
    adapt_gtsqa_triple,
)
from ark_v1.graph.graph_interface import GraphInterface


class TestGTSQAAdapter(unittest.TestCase):
    def test_adapt_single_triple(self):
        source = [
            "Silicon Graphics (Q623459)",
            "founded by (P112)",
            "James H. Clark (Q1373397)",
        ]

        converted = adapt_gtsqa_triple(source)

        self.assertEqual(
            converted,
            [
                "Silicon Graphics (Q623459)",
                "James H. Clark (Q1373397)",
                "founded by (P112)",
            ],
        )

    def test_original_triple_is_not_modified(self):
        source = ["A", "relation", "B"]

        adapt_gtsqa_triple(source)

        self.assertEqual(source, ["A", "relation", "B"])

    def test_rejects_wrong_triple_length(self):
        with self.assertRaises(ValueError):
            adapt_gtsqa_triple(["A", "relation"])

    def test_rejects_non_string_field(self):
        with self.assertRaises(TypeError):
            adapt_gtsqa_triple(["A", 123, "B"])

    def test_rejects_empty_field(self):
        with self.assertRaises(ValueError):
            adapt_gtsqa_triple(["A", "", "B"])

    def test_adapt_sample(self):
        source = {
            "id": 1,
            "question": "Test question",
            "graph": [
                ["A", "relation", "B"],
                ["B", "another relation", "C"],
            ],
        }

        converted = adapt_gtsqa_sample(source)

        self.assertEqual(
            converted["graph"],
            [
                ["A", "B", "relation"],
                ["B", "C", "another relation"],
            ],
        )

        self.assertEqual(
            source["graph"],
            [
                ["A", "relation", "B"],
                ["B", "another relation", "C"],
            ],
        )

    def test_all_development_samples(self):
        project_root = Path(__file__).resolve().parents[3]
        dataset_path = (
            project_root
            / "Dataset"
            / "gtsqa_development_agent_input.jsonl"
        )

        sample_count = 0

        with dataset_path.open("r", encoding="utf-8") as file:
            for line_number, line in enumerate(file, start=1):
                sample = json.loads(line)
                original_graph_size = len(sample["graph"])

                converted = adapt_gtsqa_sample(sample)

                self.assertEqual(
                    len(converted["graph"]),
                    original_graph_size,
                    msg=f"Graph size changed on JSONL line {line_number}.",
                )

                sample_count += 1

        self.assertEqual(sample_count, 12)

    def test_adapted_triple_keeps_meaning_after_graph_load(self):
        source = [
            "Silicon Graphics (Q623459)",
            "founded by (P112)",
            "James H. Clark (Q1373397)",
        ]

        adapted = adapt_gtsqa_triple(source)

        graph_interface = GraphInterface()
        graph_interface.graph.clear()

        try:
            graph_interface.load_graph_data([adapted])

            retrieved = graph_interface.graph.get_triples(
                "Silicon Graphics (Q623459)"
            )

            self.assertEqual(len(retrieved), 1)

            head, edge_data, tail = retrieved[0]

            self.assertEqual(
                head,
                "Silicon Graphics (Q623459)",
            )
            self.assertEqual(
                edge_data["relation"],
                "founded by (P112)",
            )
            self.assertEqual(
                tail,
                "James H. Clark (Q1373397)",
            )
        finally:
            graph_interface.graph.clear()

    def test_graph_preserves_multiple_relations_between_same_nodes(self):
        source_triples = [
            ["Entity A", "relation 1", "Entity B"],
            ["Entity A", "relation 2", "Entity B"],
        ]

        adapted_triples = [
            adapt_gtsqa_triple(triple)
            for triple in source_triples
        ]

        graph_interface = GraphInterface()
        graph_interface.graph.clear()

        try:
            graph_interface.load_graph_data(adapted_triples)

            retrieved = graph_interface.graph.get_triples("Entity A")

            self.assertEqual(len(retrieved), 2)

            retrieved_relations = {
                edge_data["relation"]
                for _, edge_data, _ in retrieved
            }

            self.assertEqual(
                retrieved_relations,
                {"relation 1", "relation 2"},
            )
        finally:
            graph_interface.graph.clear()

    def test_triple_exist_checks_each_parallel_edge(self):
        graph_interface = GraphInterface()
        graph_interface.graph.clear()

        try:
            graph_interface.load_graph_data(
                [
                    ["Entity A", "Entity B", "relation 1"],
                    ["Entity A", "Entity B", "relation 2"],
                ]
            )

            self.assertTrue(
                graph_interface.graph.triple_exist(
                    "Entity A",
                    "relation 1",
                    "Entity B",
                )
            )
            self.assertTrue(
                graph_interface.graph.triple_exist(
                    "Entity A",
                    "relation 2",
                    "Entity B",
                )
            )
            self.assertFalse(
                graph_interface.graph.triple_exist(
                    "Entity A",
                    "relation 3",
                    "Entity B",
                )
            )
        finally:
            graph_interface.graph.clear()

    def test_get_triples_can_filter_parallel_edges_by_relation(self):
        graph_interface = GraphInterface()
        graph_interface.graph.clear()

        try:
            graph_interface.load_graph_data(
                [
                    ["Entity A", "Entity B", "relation 1"],
                    ["Entity A", "Entity B", "relation 2"],
                ]
            )

            retrieved = graph_interface.graph.get_triples(
                "Entity A",
                relations=["relation 1"],
            )

            self.assertEqual(len(retrieved), 1)
            self.assertEqual(
                retrieved[0][1]["relation"],
                "relation 1",
            )
        finally:
            graph_interface.graph.clear()


if __name__ == "__main__":
    unittest.main()