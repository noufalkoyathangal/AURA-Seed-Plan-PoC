from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

def _dtype_map_for_stores() -> Dict[str, str]:
    return {
        "store_id": "string",
        "capacity": "float32",
        "footfall": "float32",
        "demo_income": "float32",
        "demo_age": "float32",
    }

def load_stores(stores_csv: str, features: List[str]) -> Tuple[pd.DataFrame, np.ndarray]:
    df = pd.read_csv(
        stores_csv,
        dtype=_dtype_map_for_stores(),
        usecols=["store_id"] + features,
        low_memory=True,
    ).dropna()
    X = df[features].astype("float32").to_numpy(copy=False)
    return df, X

def choose_k_by_silhouette(X: np.ndarray, k_min: int = 3, k_max: int = 8) -> Tuple[int, Optional[float]]:
    best_k, best_s = k_min, None
    for k in range(k_min, k_max + 1):
        if k <= 1 or k >= len(X):
            continue
        km = KMeans(n_clusters=k, n_init="auto", random_state=42)
        labels = km.fit_predict(X)
        s = silhouette_score(X, labels)
        if best_s is None or s > best_s:
            best_k, best_s = k, s
    return best_k, best_s

def run_kmeans(stores_csv: str, features: List[str], k: Optional[int]) -> Tuple[List[Dict], int, Optional[float]]:
    df, X = load_stores(stores_csv, features)
    use_k, sil = (k, None) if k else choose_k_by_silhouette(X)
    km = KMeans(n_clusters=use_k, n_init="auto", random_state=42)
    df["cluster_id"] = km.fit_predict(X)
    clusters = df[["store_id", "cluster_id"]].astype({"cluster_id": "int32"}).to_dict(orient="records")
    return clusters, use_k, sil
