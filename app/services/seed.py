from typing import Dict, List, Tuple
import pandas as pd
import numpy as np
from app.models.schemas import PlanLine

def _dtype_map_for_skus():
    return {
        "sku_id": "string",
        "category": "string",
        "cost": "float32",
        "category_score": "float32",
    }

def load_skus(skus_csv: str) -> pd.DataFrame:
    return pd.read_csv(
        skus_csv,
        dtype=_dtype_map_for_skus(),
        usecols=["sku_id", "category", "cost", "category_score"],
        low_memory=True,
    ).dropna()

def generate_seed(
    skus_csv: str,
    cluster_map: Dict[str, int],
    budget: float,
    max_skus_per_store: int,
) -> Tuple[List[PlanLine], float]:
    skus = load_skus(skus_csv).sort_values("category_score", ascending=False)
    lines: List[PlanLine] = []
    budget_left = float(budget)

    costs = skus["cost"].to_numpy(dtype="float32", copy=False)
    sku_ids = skus["sku_id"].to_numpy(dtype="object", copy=False)

    for store_id, cluster_id in cluster_map.items():
        picked = 0
        for i, sku in enumerate(sku_ids):
            c = float(costs[i])
            if picked >= max_skus_per_store:
                break
            if budget_left - c < 0:
                break
            lines.append(PlanLine(
                store_id=str(store_id),
                sku_id=str(sku),
                qty=1,
                rationale=f"cluster {cluster_id} priority"
            ))
            budget_left -= c
            picked += 1

    return lines, budget_left
