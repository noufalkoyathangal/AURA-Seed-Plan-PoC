from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    ClusterRequest, ClusterResponse,
    SeedRequest, SeedResponse,
    ValidateRequest, ValidateResponse,
    PublishRequest, PublishResponse,
    ExportRequest, ExportResponse,
)
from app.services.clustering import run_kmeans
from app.services.seed import generate_seed
from app.services.constraints import check_constraints
from app.services.exporter import export_plan_to_csv
from app.storage.repo import save_plan, get_plan
from app.orchestration.graph import graph

router = APIRouter(prefix="/api")

@router.post("/seed/cluster", response_model=ClusterResponse, tags=["seed", "clustering"])
def api_cluster(req: ClusterRequest):
    try:
        clusters, k_used, sil = run_kmeans(req.stores_csv, req.features, req.k)
        return ClusterResponse(clusters=clusters, silhouette=sil, k=k_used)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/seed/generate", response_model=SeedResponse, tags=["seed"])
def api_generate(req: SeedRequest):
    try:
        lines, budget_left = generate_seed(
            req.skus_csv, req.cluster_map, req.budget, req.max_skus_per_store
        )
        return SeedResponse(lines=lines, budget_left=budget_left)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/seed/validate", response_model=ValidateResponse, tags=["seed", "constraints"])
def api_validate(req: ValidateRequest):
    try:
        violations = check_constraints(req.lines, req.budget, req.max_skus_per_store, req.capacity_csv)
        return ValidateResponse(violations=violations, ok=len(violations) == 0)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/seed/publish", response_model=PublishResponse, tags=["seed"])
def api_publish(req: PublishRequest):
    try:
        plan_id, version, status = save_plan(req.plan_name, [l.model_dump() for l in req.lines])
        return PublishResponse(plan_id=plan_id, version=version, status=status)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/export/erp", response_model=ExportResponse, tags=["export"])
def api_export(req: ExportRequest):
    plan = get_plan(req.plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    path = export_plan_to_csv(req.plan_id, [type("PL", (), l) for l in plan["lines"]])
    return ExportResponse(path=path)

@router.post("/seed/auto", tags=["workflow"])
def api_seed_auto(req: SeedRequest):
    """
    Orchestrate: cluster -> generate -> validate -> export (if no violations).
    """
    initial = {
        "stores_csv": "data/stores.csv",        # could be parameterized
        "skus_csv": req.skus_csv,
        "features": ["capacity", "footfall"],
        "k": None,
        "budget": req.budget,
        "max_skus_per_store": req.max_skus_per_store,
        "cluster_map": {},
        "lines": [],
        "violations": [],
        "export_path": None,
    }
    result = graph.invoke(initial)
    return result
