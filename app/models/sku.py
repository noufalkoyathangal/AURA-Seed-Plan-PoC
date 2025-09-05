from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from decimal import Decimal

class SKU(BaseModel):
    sku_id: str = Field(..., description="Unique SKU identifier")
    style: str = Field(..., description="Product style")
    color: str = Field(..., description="Product color")
    size: str = Field(..., description="Product size")
    cost: Decimal = Field(..., description="Unit cost")
    lifecycle_status: str = Field(..., description="Product lifecycle stage")
    attributes: Dict = Field(default_factory=dict)

class PlanningConstraints(BaseModel):
    budget: Decimal = Field(..., description="Total budget limit")
    max_skus_per_store: int = Field(..., description="Maximum SKUs per store")
    min_skus_per_store: int = Field(1, description="Minimum SKUs per store")
    fixture_constraints: Dict = Field(default_factory=dict)

class SeedPlanRequest(BaseModel):
    skus_csv: str = Field(..., description="Path to SKUs CSV file")
    cluster_map: Dict[str, int] = Field(..., description="Store cluster mapping")
    constraints: PlanningConstraints = Field(..., description="Planning constraints")
    use_forecasting: bool = Field(True, description="Enable demand forecasting")
class AutoSeedPlanRequest(BaseModel):
    skus_csv: str = Field(..., description="Path to SKUs CSV file")
    budget: float = Field(..., description="Total budget limit")
    max_skus_per_store: int = Field(25, description="Maximum SKUs per store")
    use_forecasting: bool = Field(True, description="Enable demand forecasting")
    
    # Auto-generation parameters
    clustering_features: List[str] = Field(default=["capacity", "footfall"])
    clustering_algorithm: str = Field(default="kmeans")
    n_clusters: Optional[int] = Field(None, description="Auto-detect if not provided")
    
    # Optional overrides (for advanced users)
    cluster_map: Optional[Dict[str, int]] = Field(None, description="Pre-defined clusters")
    custom_constraints: Optional[Dict] = Field(None, description="Custom constraints")

class AutoSeedPlanResult(BaseModel):
    task_id: str = Field(..., description="Background task identifier")
    status: str = Field(..., description="Task status")
    estimated_completion: Optional[str] = Field(None)


class SeedPlanResult(BaseModel):
    plan_id: str = Field(..., description="Generated plan identifier")
    lines: List[Dict] = Field(..., description="Planning lines")
    total_cost: Decimal = Field(..., description="Total plan cost")
    coverage_stats: Dict = Field(..., description="Coverage statistics")
    confidence_scores: Dict = Field(..., description="Confidence by line")
