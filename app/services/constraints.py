from typing import List, Dict
import pandas as pd
from collections import defaultdict
from app.models.schemas import PlanLine, Violation

def check_constraints(
    lines: List[PlanLine],
    budget: float,
    max_skus_per_store: int,
    capacity_csv: str | None = None,
) -> List[Violation]:
    violations: List[Violation] = []

    # Budget check
    df = pd.DataFrame([l.model_dump() for l in lines])
    if not df.empty:
        # Quantities are small; if cost needed, plug actual cost join here
        est_cost = len(df)  # each qty=1, cost joined later; PoC keeps it simple
        if est_cost > budget + 1e-6:
            violations.append(Violation(
                code="BUDGET_EXCEEDED",
                message=f"Estimated items {est_cost} exceed budget {budget}",
                suggestion="Reduce low-priority SKUs or increase budget",
            ))

    # Max SKUs per store
    count_by_store: Dict[str, int] = defaultdict(int)
    for l in lines:
        count_by_store[l.store_id] += 1
    for s, cnt in count_by_store.items():
        if cnt > max_skus_per_store:
            violations.append(Violation(
                code="MAX_SKU_PER_STORE",
                message=f"Store {s} has {cnt} SKUs over limit {max_skus_per_store}",
                suggestion="Lower max or remove lowest-score SKUs",
            ))

    # Capacity optional check (placeholder)
    if capacity_csv:
        try:
            cap = pd.read_csv(capacity_csv, usecols=["store_id", "capacity"], dtype={"store_id": "string", "capacity": "float32"})
            cap_map = dict(zip(cap["store_id"], cap["capacity"]))
            for s, cnt in count_by_store.items():
                c = cap_map.get(s)
                if c is not None and cnt > c:
                    violations.append(Violation(
                        code="CAPACITY_LIMIT",
                        message=f"Store {s} items {cnt} exceed capacity {c}",
                        suggestion="Raise capacity or reduce items",
                    ))
        except Exception:
            violations.append(Violation(
                code="CAPACITY_LOAD_ERROR",
                message="Could not load capacity CSV",
                suggestion="Verify CSV schema: store_id, capacity",
            ))

    return violations
