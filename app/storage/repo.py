import os
import json
import time
from typing import Any, Dict, Tuple
from app.core.config import settings

PLANS_FILE = os.path.join(settings.out_dir, "plans.json")

def _ensure_dirs():
    os.makedirs(settings.out_dir, exist_ok=True)
    if not os.path.exists(PLANS_FILE):
        with open(PLANS_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)

def save_plan(plan_name: str, lines: list[dict]) -> Tuple[str, int, str]:
    _ensure_dirs()
    with open(PLANS_FILE, "r", encoding="utf-8") as f:
        plans = json.load(f)

    plan_id = str(int(time.time()))
    version = 1
    plans[plan_id] = {
        "name": plan_name,
        "version": version,
        "status": "published",
        "lines": lines,
        "ts": time.time(),
    }

    with open(PLANS_FILE, "w", encoding="utf-8") as f:
        json.dump(plans, f, indent=2)

    return plan_id, version, "published"

def get_plan(plan_id: str) -> Dict[str, Any] | None:
    _ensure_dirs()
    with open(PLANS_FILE, "r", encoding="utf-8") as f:
        plans = json.load(f)
    return plans.get(plan_id)
