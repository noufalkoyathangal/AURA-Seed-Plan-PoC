from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum

class ClusteringAlgorithm(str, Enum):
    KMEANS = "kmeans"
    FUZZY_CMEANS = "fuzzy_cmeans"

class Store(BaseModel):
    store_id: str = Field(..., description="Unique store identifier")
    capacity: int = Field(..., description="Maximum SKU capacity")
    footfall: int = Field(..., description="Average daily customer traffic")
    demographics: Dict = Field(default_factory=dict)
    cluster_id: Optional[int] = None

class StoreClusterRequest(BaseModel):
    stores_csv: str = Field(..., description="Path to stores CSV file")
    features: List[str] = Field(..., description="Features for clustering")
    algorithm: ClusteringAlgorithm = Field(ClusteringAlgorithm.KMEANS)
    n_clusters: Optional[int] = None

class ClusterResult(BaseModel):
    cluster_map: Dict[str, int] = Field(..., description="Store to cluster mapping")
    silhouette_score: float = Field(..., description="Clustering quality score")
    cluster_stats: Dict = Field(..., description="Statistics per cluster")
    confidence: float = Field(..., description="Overall confidence score")
