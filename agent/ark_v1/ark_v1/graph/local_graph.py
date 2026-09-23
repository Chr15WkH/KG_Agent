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
        self.indexed_nodes = []
        self.relation_embeddings = None
        self.relation_index = None
        self.indexed_relations = []

    def clear(self):
        self.graph.clear()

        self.node_embeddings = None
        self.node_index = None
        self.indexed_nodes = []

        self.relation_embeddings = None
        self.relation_index = None
        self.indexed_relations = []
        
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

        self.indexed_nodes = list(nodes)

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

        self.indexed_relations = list(relations)

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
        for index, score in zip(I[0], D[0]):
            index = int(index)

            if index < 0:
                continue

            results.append(
                {
                    "node": self.indexed_nodes[index],
                    "distance": float(score),
                }
            )
        return results

    def get_close_relations(self, query: str, k: int = 5) -> List[Dict]:
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
        for index, score in zip(I[0], D[0]):
            index = int(index)

            if index < 0:
                continue

            results.append(
                {
                    "relation": self.indexed_relations[index],
                    "distance": float(score),
                }
            )

        return results

    def get_triples(
        self,
        head: str,
        relations: Optional[List[str]] = None,
        direction: str = "outgoing",
    ) -> List:
        """
        Get triples in the selected direction relative to the anchor.
        The parameter 'head' is retained for compatibility and represents
        the anchor entity. Returned triples preserve their original direction.
        """
        if direction not in ("outgoing", "incoming"):
            raise ValueError(
                "direction must be 'outgoing' or 'incoming'"
            )

        if direction == "outgoing":
            edges = self.graph.out_edges(head, data=True)
        else:
            edges = self.graph.in_edges(head, data=True)

        triples = []
        for source, target, edge_data in edges:
            if (
                relations is None
                or edge_data["relation"] in relations
            ):
                triples.append([source, edge_data, target])

        return triples

    def get_relations(
        self,
        head: str,
        direction: str = "outgoing",
    ) -> List[str]:
        """Get relation names for a given entity in the selected direction."""
        return [
            edge_data["relation"]
            for edge_data in self.get_edges(
                head,
                direction=direction,
            )
        ]

    def get_edges(
        self,
        head: str,
        direction: str = "outgoing",
    ) -> List[Dict]:
        """Get relation candidates with directions relative to the anchor."""
        if direction not in ("outgoing", "incoming", "both"):
            raise ValueError(
                "direction must be 'outgoing', 'incoming', or 'both'"
            )

        results = []

        if direction in ("outgoing", "both"):
            for _, _, edge_data in self.graph.out_edges(
                head,
                data=True,
            ):
                results.append({
                    **edge_data,
                    "direction": "outgoing",
                })

        if direction in ("incoming", "both"):
            for _, _, edge_data in self.graph.in_edges(
                head, data=True
            ):
                results.append({
                    **edge_data,
                    "direction": "incoming",
                })

        return results

    def entities_exist(self, entities: List[str]) -> List[bool]:
        """Check if the entities exist in the graph."""
        return [entity in self.graph for entity in entities]

    def relations_exist(
        self,
        relations: List[str],
        head: Optional[str] = None,
        direction: str = "outgoing",
    ) -> List[bool]:
        """
        Check relations in the selected direction relative to the anchor.
        If head is None, check relation existence across the whole graph.
        """
        if direction not in ("outgoing", "incoming"):
            raise ValueError(
                "direction must be 'outgoing' or 'incoming'"
            )

        if head is None:
            edges = self.graph.edges(data=True)
        elif direction == "outgoing":
            edges = self.graph.out_edges(head, data=True)
        else:
            edges = self.graph.in_edges(head, data=True)

        available_relations = {
            edge_data["relation"]
            for _, _, edge_data in edges
        }

        return [
            relation in available_relations
            for relation in relations
        ]