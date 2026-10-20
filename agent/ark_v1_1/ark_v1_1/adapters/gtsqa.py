from typing import Any, Dict, List


def adapt_gtsqa_triple(triple: List[str]) -> List[str]:
    """Convert one GTSQA triple to the format expected by ARK v1.

    GTSQA format:
        [head, relation, tail]

    ARK v1 string format:
        [head, tail, relation]
    """
    if not isinstance(triple, list):
        raise TypeError("A GTSQA triple must be a list.")

    if len(triple) != 3:
        raise ValueError(
            f"A GTSQA triple must contain exactly three elements, got {len(triple)}."
        )

    head, relation, tail = triple

    for field_name, value in (
        ("head", head),
        ("relation", relation),
        ("tail", tail),
    ):
        if not isinstance(value, str):
            raise TypeError(
                f"The triple field '{field_name}' must be a string, "
                f"got {type(value).__name__}."
            )

        if not value.strip():
            raise ValueError(
                f"The triple field '{field_name}' must not be empty."
            )

    return [head, tail, relation]


def adapt_gtsqa_sample(sample: Dict[str, Any]) -> Dict[str, Any]:
    """Convert the graph in one GTSQA Agent Input sample.

    The original sample is not modified.
    """
    required_fields = ("id", "question", "graph")

    for field_name in required_fields:
        if field_name not in sample:
            raise ValueError(
                f"GTSQA sample is missing required field '{field_name}'."
            )

    if not isinstance(sample["graph"], list):
        raise TypeError("The GTSQA sample field 'graph' must be a list.")

    converted_graph = []

    for triple_index, triple in enumerate(sample["graph"]):
        try:
            converted_graph.append(adapt_gtsqa_triple(triple))
        except (TypeError, ValueError) as error:
            raise ValueError(
                f"Invalid triple at graph index {triple_index}: {error}"
            ) from error

    return {
        **sample,
        "graph": converted_graph,
    }