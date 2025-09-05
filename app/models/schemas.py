from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class ClusterRequest(BaseModel):
    stores_csv: str = Field(..., description="Path to stores CSV, e.g., data/stores.csv")
    features: List[str] = Field(default_factory=lambda: ["capacity", "footfall"])
    k: Optional[int] = Field(None, description="If not set, use best k by silhouette in [3..8]")
    period: Optional[str] = Field(None, description="For UI/info only")

class ClusterResponse(BaseModel):
    clusters: List[Dict]
    silhouette: Optional[float] = None
    k: int

class SeedRequest(BaseModel):
    skus_csv: str = Field(..., description="Path to SKUs CSV")
    cluster_map: Dict[str, int] = Field(..., description="store_id -> cluster_id")
    budget: float
    max_skus_per_store: int = 200

class PlanLine(BaseModel):
    store_id: str
    sku_id: str
    qty: int
    rationale: str

class SeedResponse(BaseModel):
    lines: List[PlanLine]
    budget_left: float

class ValidateRequest(BaseModel):
    lines: List[PlanLine]
    budget: float
    max_skus_per_store: int = 200
    capacity_csv: Optional[str] = None

class Violation(BaseModel):
    code: str
    message: str
    suggestion: Optional[str] = None

class ValidateResponse(BaseModel):
    violations: List[Violation]
    ok: bool

class PublishRequest(BaseModel):
    plan_name: str
    lines: List[PlanLine]

class PublishResponse(BaseModel):
    plan_id: str
    version: int
    status: str

class ExportRequest(BaseModel):
    plan_id: str
    format: str = "csv"

class ExportResponse(BaseModel):
    path: str
