from app.labs.ncmi.model import build_mismatched_node_sets, weighted_interpolation


def run_ncmi_experiment(size_a: int = 5, size_b: int = 8) -> dict:
    set_a, set_b = build_mismatched_node_sets(size_a, size_b)
    interpolated = weighted_interpolation(set_a, set_b)
    return {
        "set_a": set_a.nodes,
        "set_b": set_b.nodes,
        "interpolated": interpolated,
        "metadata": {
            "size_a": size_a,
            "size_b": size_b,
            "type": "ncmi_weighted_interpolation",
        },
    }
