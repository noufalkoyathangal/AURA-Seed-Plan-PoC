import os
import time
import pandas as pd
from app.core.config import settings
from app.models.schemas import PlanLine

def export_plan_to_csv(plan_id: str, lines: list[PlanLine]) -> str:
    os.makedirs(settings.out_dir, exist_ok=True)
    ts = int(time.time())
    path = os.path.join(settings.out_dir, f"{plan_id}_{ts}.csv")
    df = pd.DataFrame([l.model_dump() for l in lines])
    df.to_csv(path, index=False)
    return path
