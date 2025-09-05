from typing import TypedDict, List, Dict, Optional
from langgraph.graph import StateGraph
from app.services.clustering import run_kmeans
from app.services.seed import generate_seed
from app.services.constraints import check_constraints
from app.services.exporter import export_plan_to_csv

class SeedState(TypedDict):
    stores_csv: str
    skus_csv: str
    features: List[str]
    k: Optional[int]
    budget: float
    max_skus_per_store: int
    cluster_map: Dict[str, int]
    lines: List[dict]
    violations: List[dict]
    export_path: Optional[str]

def node_cluster(state: SeedState) -> dict:
    clusters, k_used, _sil = run_kmeans(state["stores_csv"], state["features"], state["k"])
    return {
        "cluster_map": {c["store_id"]: int(c["cluster_id"]) for c in clusters}
    }

def node_generate(state: SeedState) -> dict:
    lines, _budget_left = generate_seed(
        skus_csv=state["skus_csv"],
        cluster_map=state["cluster_map"],
        budget=state["budget"],
        max_skus_per_store=state["max_skus_per_store"],
    )
    return {"lines": [l.model_dump() for l in lines]}

def node_validate(state: SeedState) -> dict:
    # Convert dicts back to simple objects compatible with check_constraints
    violations = check_constraints(
        lines=[type("PL", (), l) for l in state["lines"]],
        budget=state["budget"],
        max_skus_per_store=state["max_skus_per_store"],
        capacity_csv=None,
    )
    return {"violations": [v.model_dump() for v in violations]}

def node_export(state: SeedState) -> dict:
    # If violations exist, skip export and return None
    if state["violations"]:
        return {"export_path": None}
    path = export_plan_to_csv("seed_auto", [type("PL", (), l) for l in state["lines"]])
    return {"export_path": path}

def build_graph():
    builder = StateGraph(SeedState)

    # Nodes
    builder.add_node("cluster", node_cluster)
    builder.add_node("generate", node_generate)
    builder.add_node("validate", node_validate)
    builder.add_node("export", node_export)

    # Entry and edges
    builder.set_entry_point("cluster")
    builder.add_edge("cluster", "generate")
    builder.add_edge("generate", "validate")
    builder.add_edge("validate", "export")

    # Explicitly mark terminal node to avoid "dead-end" validation errors
    builder.set_finish_point("export")

    return builder.compile()

graph = build_graph()
