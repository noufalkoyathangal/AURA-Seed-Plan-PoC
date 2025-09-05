# AURA Seed Plan Agent — Technical Design & Implementation

[![Docker](https://img.shields.io/badge/docker-ready-blue)](https://www.docker.com/)

---

## 📋 Table of Contents

* [Executive Summary](#executive-summary)
* [Technology Stack](#technology-stack)
* [Project Structure](#project-structure)
* [Quick Start Guide](#quick-start-guide)
* [Problem Statement & Business Context](#problem-statement--business-context)
* [Technical Architecture](#technical-architecture)
* [API Documentation](#api-documentation)
* [Testing & Examples](#testing--examples)
* [Deployment](#deployment)
* [Work Breakdown & Roadmap](#work-breakdown--roadmap)
* [Interview Q\&A](#interview-qa)
* [Troubleshooting](#troubleshooting)
* [Contributing](#contributing)
* [Key Achievements](#key-achievements)

---

## Executive Summary

This PoC showcases the **Seed Plan Agent** from Intelo’s AURA suite. It focuses on automating assortment planning using store clustering, seed generation with constraints, and guardrail validation. The system is built on **FastAPI**, packaged with **Docker**, and designed to demonstrate how AURA can tackle retail planning inefficiencies outlined in the PRD.

---

## 🛠 Technology Stack

| Component        | Technology             | Purpose                           |
| ---------------- | ---------------------- | --------------------------------- |
| API Framework    | FastAPI                | Async API with built-in docs      |
| ML/Analytics     | scikit-learn, pandas   | Clustering and data wrangling     |
| Containerization | Docker, Docker Compose | Portable development & deployment |
| Orchestration    | LangGraph              | Multi-agent workflow coordination |
| Data Validation  | Pydantic               | Request/response validation       |
| Authentication   | JWT + RBAC             | Role-based security               |
| Documentation    | Swagger/OpenAPI        | Interactive API docs              |

---

## 📁 Project Structure

```
aura-seed-plan-poc/
├── app/
│   ├── models/           # Data models (Pydantic)
│   │   ├── store.py
│   │   ├── sku.py
│   │   └── user.py
│   ├── routes/           # API routes
│   │   └── router.py
│   ├── services/         # Business logic
│   │   ├── clustering.py
│   │   ├── seed.py
│   │   └── constraints.py
│   ├── auth/             # Auth & RBAC
│   │   └── rbac.py
│   └── main.py           # FastAPI entry point
├── data/                 # Example CSVs
│   ├── stores.csv
│   └── skus.csv
├── tests/                # Test suite
├── docker-compose.yml
├── Dockerfile
└── README.md
```

---

## 🚀 Quick Start Guide

### Prerequisites

* Docker + Docker Compose
* Python 3.9+ (optional for local dev)
* At least 4GB RAM (clustering needs it)

### Option 1: Run with Docker (Recommended)

```bash
git clone <repository-url>
cd aura-seed-plan-poc
docker-compose up --build
curl http://localhost:8000/health
open http://localhost:8000/docs
```

### Option 2: Local Development

```bash
pip install -r requirements.txt
export PYTHONPATH=.
uvicorn app.main:app --reload --port 8000
curl http://localhost:8000/health
```

---

## Problem Statement & Business Context

Retail assortment planning is still dominated by spreadsheets and manual decision-making, leading to **\$1+ trillion in inefficiencies annually**.
Main issues include:

* Stockouts (\~4% sales loss globally)
* Customer churn (43% leave when items are unavailable)
* Slow planning cycles (weeks of reconciling ERP/PLM/POS data)
* Disconnected strategy vs store-level execution
* Excel-heavy workflows that don’t scale

**AURA success metrics (from PRD):**

* Cut planning time significantly
* Improve SKU coverage vs line plans
* Increase forecast hit rate
* Reduce markdowns and excess stock

---

## 🏗 Technical Architecture

```
Users (Swagger UI, curl, API clients)
        ↓
 ┌───────────────────────────────────────┐
 │ Docker Container (FastAPI App)        │
 │ ┌─────────────┐  ┌──────────────────┐ │
 │ │ API Routes  │──│ Orchestration    │ │
 │ │             │  │ (LangGraph)      │ │
 │ └─────────────┘  └──────────────────┘ │
 │           ↓              ↓             │
 │ ┌────────────────────────────────────┐ │
 │ │           Services Layer           │ │
 │ │ Clustering │ Seed Plan │ Guardrails│ │
 │ └────────────────────────────────────┘ │
 └────────────────────────────────────────┘
        ↑                       ↓
     Input CSVs              Output CSVs
```

---

## 📚 API Documentation

### Health Check

```http
GET /health
```

Response:

```json
{ "status": "healthy", "timestamp": "...", "version": "1.0.0" }
```

### Store Clustering

```http
POST /api/seed/cluster
```

Request:

```json
{ "stores_csv": "data/stores.csv", "features": ["capacity","footfall"], "algorithm": "kmeans", "k": 5 }
```

### Seed Plan Generation

```http
POST /api/seed/generate
Authorization: Bearer <jwt-token>
```

Request:

```json
{
  "skus_csv": "data/skus.csv",
  "cluster_map": {"S1":0,"S2":1},
  "constraints": {"budget":50000,"max_skus_per_store":25}
}
```

---

## 🧪 Testing & Examples

CLI examples with `curl` are provided in the repo.
For Python testing:

```python
import requests
BASE = "http://localhost:8000"
headers = {"Authorization":"Bearer demo_token"}

resp = requests.post(f"{BASE}/api/seed/cluster", json={...})
print(resp.json())
```

---

## 🚀 Deployment

### Docker

```yaml
services:
  aura-api:
    build: .
    ports: ["8000:8000"]
    restart: unless-stopped
```

### Kubernetes

Sample `Deployment` manifest is included for scaling with 3 replicas and health probes.

---

## Roadmap

* **Epic 1:** Data foundations & validation
* **Epic 2:** ML & analytics engine (multi-cluster algorithms, demand forecasting)
* **Epic 3:** Collaboration (draft/review workflows, comments, RBAC)
* **Epic 4:** Scale & ERP/BI integrations

---

## 🎯 Interview Q\&A

Sample technical and business questions are included (covering data consistency, caching, ML drift handling, explainability, ROI measurement, adoption strategy).

---

## 🔧 Troubleshooting

* **Docker port in use →** kill process or use a different port
* **Memory errors →** increase Docker memory or sample datasets
* **403 Forbidden →** check JWT and RBAC roles

---

## 🤝 Contributing

1. Install dev dependencies
2. Run pre-commit hooks
3. Use `black`, `flake8`, `mypy` for quality
4. Keep test coverage >80%

---

## 🏆 Key Achievements

* Production-ready PoC with FastAPI + Docker
* ML-driven clustering and seed generation
* JWT-based security
* Robust testing setup
* Designed for ERP/BI integration
* Scalable for 100k+ SKUs

