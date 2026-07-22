from dataclasses import dataclass
from typing import List

@dataclass
class CircularNodeSet:
    nodes: List[float]


def build_mismatched_node_sets(size_a: int, size_b: int) -> tuple[CircularNodeSet, CircularNodeSet]:
    set_a = CircularNodeSet(nodes=[float(i) for i in range(size_a)])
    set_b = CircularNodeSet(nodes=[float(i * 1.5 + 0.5) for i in range(size_b)])
    return set_a, set_b


def weighted_interpolation(set_a: CircularNodeSet, set_b: CircularNodeSet) -> list[float]:
    max_len = max(len(set_a.nodes), len(set_b.nodes))
    weights = []
    for i in range(max_len):
        a = set_a.nodes[i % len(set_a.nodes)]
        b = set_b.nodes[i % len(set_b.nodes)]
        weights.append((a * 0.6 + b * 0.4) / (1.0 + abs(a - b)))
    return weights
