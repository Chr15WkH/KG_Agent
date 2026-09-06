import networkx as nx
from typing import Optional, List, Dict
from sentence_transformers import SentenceTransformer
import faiss


class LocalGraph:
    def __init__(self):
        self.graph = nx.MultiDiGraph()
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        self.node_embeddings = None
        self.node_index = None
        self.relation_embeddings = None
        self.relation_index = None

    def clear(self):
        self.graph.clear()

    def vectorize(self, head_nodes_only: bool = True):
        """Use a sentence transformer to create embeddings for each node and relation."""

        # get all nodes that are a head of an edge
        if not self.graph.nodes:
            raise ValueError("Graph is empty. Cannot vectorize an empty graph.")
        if not self.graph.edges:
            raise ValueError("Graph has no edges. Cannot vectorize without edges.")

        if head_nodes_only:
            nodes = [n for n in self.graph.nodes() if self.graph.out_degree(n) > 0]
        else:
            nodes = list(self.graph.nodes())
        if not nodes:
            raise ValueError("No head nodes found in the graph.")

        self.node_embeddings = self.embedding_model.encode(
            nodes, normalize_embeddings=True, convert_to_numpy=True
        )
        self.node_index = faiss.IndexFlatIP(self.node_embeddings.shape[1])
        self.node_index.add(self.node_embeddings)
        relations = list(
            set(
                edge_data["relation"] for _, _, edge_data in self.graph.edges(data=True)
            )
        )
        self.relation_embeddings = self.embedding_model.encode(
            relations, normalize_embeddings=True, convert_to_numpy=True
        )
        self.relation_index = faiss.IndexFlatIP(self.relation_embeddings.shape[1])
        self.relation_index.add(self.relation_embeddings)

        # print(f"Node embeddings shape: {self.node_embeddings.shape}")
        # print(f"Relation embeddings shape: {self.relation_embeddings.shape}")

    def add_triple(self, head, tail, **metadata):
        """Add a triple to the graph."""
        self.graph.add_edge(head, tail, **metadata)

    def triple_exist(self, head, relation, tail) -> bool:
        """Check if a triple exists in the graph."""
        if not self.graph.has_edge(head, tail):
            return False

        edges_between_nodes = self.graph.get_edge_data(head, tail)

        return any(
            edge_data.get("relation") == relation
            for edge_data in edges_between_nodes.values()
        )

    def get_close_nodes(self, query: str, k: int = 5) -> List[Dict]:
        """Get the k closest nodes to the query string based on embeddings."""
        if self.node_embeddings is None:
            raise ValueError(
                "Node embeddings are not initialized. Call vectorize() first."
            )

        query_vec = self.embedding_model.encode(
            [query], normalize_embeddings=True, convert_to_numpy=True
        )
        D, I = self.node_index.search(query_vec, k)

        results = []
        nodes = list(self.graph.nodes())
        for i in range(len(I[0])):
            results.append(
                {
                    "node": nodes[int(I[0][i])],
                    "distance": float(D[0][i]),
                }
            )
        return results

    def get_close_relations(self, query: str, k: int = 5) -> Dict:
        """Get the k closest relations to the query string based on embeddings."""
        if self.relation_embeddings is None:
            raise ValueError(
                "Relation embeddings are not initialized. Call vectorize() first."
            )

        query_vec = self.embedding_model.encode(
            [query], normalize_embeddings=True, convert_to_numpy=True
        )
        D, I = self.relation_index.search(query_vec, k)

        results = []
        relations = list(
            set(
                edge_data["relation"] for _, _, edge_data in self.graph.edges(data=True)
            )
        )
        for i in range(len(I[0])):
            results.append(
                {
                    "relation": relations[int(I[0][i])],
                    "distance": float(D[0][i]),
                }
            )
        return results

    def get_triples(
        self,
        head: str,
        relations: Optional[List[str]] = None,
    ) -> List:
        """Get outgoing triples for a head and optional relations."""
        triples = []

        for _, tail, edge_data in self.graph.out_edges(
            head,
            data=True,
        ):
            if (
                relations is None
                or edge_data["relation"] in relations
            ):
                triples.append([head, edge_data, tail])

        return triples

    def get_relations(self, head) -> List[str]:
        """Get outgoing relations for a given entity."""
        return [
            edge_data["relation"]
            for _, _, edge_data in self.graph.out_edges(
                head,
                data=True,
            )
        ]

    def get_edges(self, head: str) -> List[Dict]:
        """Get outgoing edges for a given head node."""
        return [
            edge_data
            for _, _, edge_data in self.graph.out_edges(
                head,
                data=True,
            )
        ]

    def entities_exist(self, entities: List[str]) -> List[bool]:
        """Check if the entities exist in the graph."""
        return [entity in self.graph for entity in entities]

    def relations_exist(
        self, relations: List[str], head: Optional[str] = None
    ) -> List[bool]:
        """Check if the relations exist in the graph."""
        if head is not None:
            return [
                any(
                    edge_data["relation"] == relation
                    for _, _, edge_data in self.graph.edges(head, data=True)
                )
                for relation in relations
            ]
        else:
            return [
                any(
                    edge_data["relation"] == relation
                    for _, _, edge_data in self.graph.edges(data=True)
                )
                for relation in relations
            ]
