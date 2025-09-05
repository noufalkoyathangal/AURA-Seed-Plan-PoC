# AURA Seed Plan PoC — FastAPI Service

## Overview
This PoC demonstrates a pre-season retail planning workflow that generates a data-driven draft assortment, validates it against guardrails, and exports artifacts, aligning with the Seed Plan Agent in Intelo’s AURA suite.
Retailers often face stockouts, overstocks, and long planning cycles due to fragmented, spreadsheet-heavy processes; this PoC addresses those issues by automating clustering, seed generation, constraint checks, and export, with humans-in-the-loop for approvals.

## The problem
Assortment and allocation planning is slow, siloed, and manual, leading to stockouts in high-demand stores, overstocks elsewhere, markdowns, and missed responses to local events and trends.
The core issue is overreliance on intuition and spreadsheets across PLM/ERP/POS, causing delays, bias, and poor alignment between strategy and store-level execution.

## The solution in this PoC
A single FastAPI microservice orchestrates a linear workflow: cluster stores → generate a budget-aware seed plan → validate guardrails → export, mirroring Seed Plan Agent capabilities in the PRD.
This focuses on temporal efficiency, explainability, and guardrail compliance, preparing the path for more advanced agents (Scenarios, Buy Plan & PO, Pre-Allocation) to be layered next.

## Why this design
- FastAPI gives a clean HTTP surface with type-driven OpenAPI and simple containerization, enabling quick demos and strong contracts.
- Containerization provides portability, isolation, and repeatability across dev/test/prod, with a minimal Python base image and a simple Uvicorn entrypoint.
- Linear workflow orchestration keeps this PoC deterministic and easy to reason about, aligning with the PRD’s guardrails-first, human-in-the-loop philosophy.
- CSV-based inputs/outputs keep setup friction low while still demonstrating the Seed Plan data flow; this can evolve to ERP/PLM integrations without changing external APIs.

## Architecture
This service maps to Intelo’s high-level architecture as an agentic backend node that exposes HTTP endpoints, orchestrates planning steps, and can emit exports for downstream adapters.
At a high level, it consists of: API (FastAPI), Orchestration (workflow steps), Services (clustering, seed generation, constraints, exporter), and Data/Artifacts (CSV inputs and outputs).

### Component responsibilities
- API: Defines routes for each step and a one-shot endpoint to run the entire flow for demo and testing.
- Orchestration: Executes a linear sequence cluster → generate → validate → export to keep the demo deterministic and easy to present.
- Services:  
  - Clustering: Groups stores (e.g., K-means) by behavior/features to reflect buying patterns at cluster-level granularity.
  - Seed Generation: Creates a draft SKU × store/cluster quantity plan under budget and max SKU limits.
  - Constraints: Enforces budget caps and SKU-per-store caps, and surfaces violations consistent with PRD guardrails.
  - Export: Produces CSV artifacts for simple handoffs or ERP pushes in later iterations.

### Repository layout (key files)
- app/main.py — FastAPI app bootstrap and routing.
- app/api/routes.py — HTTP endpoints for cluster/generate/validate/export and a one-shot flow.
- app/orchestration/graph.py — Step-by-step workflow wiring for cluster → generate → validate → export.
- app/services/* — Clustering, seed generation, constraint checking, and export helpers.
- data/* and out/* — Example CSV inputs and generated CSV outputs, respectively.

## How to run with Docker
- Build the image from the project root: docker build -t aura-seed-poc . to supply the current directory as build context.
- Run the container: docker run --rm -p 8000:8000 aura-seed-poc to publish the API on port 8000.
- Alternatively, use Compose: docker compose up --build to rebuild and launch using the provided docker-compose.yml.
- After startup, exercise endpoints with curl or open the interactive docs at /docs on port 8000 for live testing and schema inspection.

## Endpoints
- Health: GET /health — quick status check to verify container and app are running.
- Cluster: POST /api/seed/cluster — cluster stores by selected features; returns store_id → cluster_id mapping.
- Generate: POST /api/seed/generate — create a draft seed plan under budget and max SKU caps per store/cluster.
- Validate: POST /api/seed/validate — enforce guardrails and return violations/suggestions if any.
- Export: POST /api/export/erp — export current plan as CSV artifact for downstream handoff.
- One-shot: POST /api/seed/auto — run cluster → generate → validate → export in a single call and return the export artifact path if valid.

## Test with curl (Windows-safe quoting)
- Cluster stores:
```
curl -X POST http://127.0.0.1:8000/api/seed/cluster ^
  -H "Content-Type: application/json" ^
  -d "{""stores_csv"":""data/stores.csv"",""features"":[""capacity"",""footfall""]}"
```
- Generate draft plan:
```
curl -X POST http://127.0.0.1:8000/api/seed/generate ^
  -H "Content-Type: application/json" ^
  -d "{""skus_csv"":""data/skus.csv"",""cluster_map"":{""S1"":0,""S2"":1}, ""budget"":200, ""max_skus_per_store"":3}"
```
- Validate guardrails:
```
curl -X POST http://127.0.0.1:8000/api/seed/validate ^
  -H "Content-Type: application/json" ^
  -d "{""lines"":[{""sku"":""SKU1"",""store"":""S1"",""qty"":5}], ""budget"":200, ""max_skus_per_store"":3}"
```
- One‑shot end‑to‑end:[5]
```
curl -X POST http://127.0.0.1:8000/api/seed/auto ^
  -H "Content-Type: application/json" ^
  -d "{""skus_csv"":""data/skus.csv"",""budget"":200,""max_skus_per_store"":3}"
```

## What the demo proves
- Clustering reflects buying patterns and local context readiness from the PRD, enabling cluster-level planning that reduces manual work.
- Draft generation fits within budgets and SKU caps, aligning to guardrails and the human-in-the-loop paradigm.
- Validation surfaces violations early to prevent downstream PO or allocation issues, consistent with governance and compliance goals.
- Export artifacts provide a clean handoff to ERP/integration layers, mapping to Intelo’s high-level adapters and desks.

## Mapping to AURA PRD
- Seed Plan Agent: dynamic store clustering, draft seed plan generation, constraint-aware guardrails, editable artifacts, and exports.
- Guardrails: budget caps, SKU limits, and explainability are built into the flow with approvals before publish, as specified.
- KPIs supported by this slice: planning time reduction, SKU coverage vs. targets, and forecast/assortment alignment proxies for accuracy.

## For non-technical readers
- This system proposes the first cut of “what to stock where,” using past data and rules to suggest an initial plan faster and with fewer errors.
- It flags issues with the plan early (budget or display constraints) so teams can resolve them before committing to purchases.
- It saves time, reduces markdowns, and improves on-shelf availability by aligning supply to demand by store clusters.

## For technical readers
- A typed FastAPI app exposes endpoints for each step and a one-shot route, containerized with a slim Python base and Uvicorn entrypoint.
- The orchestration runs sequential nodes: cluster → generate → validate → export, with explicit guardrail checks and an export artifact at the end.
- CSV data inputs/outputs are used for demo simplicity; swapping to Postgres/ERP connectors would not change public API shapes.

## Runbook
- Build: docker build -t aura-seed-poc . to create the image with the current directory as context.
- Run: docker run --rm -p 8000:8000 aura-seed-poc to start the API on port 8000.
- Compose (optional): docker compose up --build to rebuild and run using the provided docker-compose.yml for mounted data/out volumes.
- Verify: call GET /health and open /docs to exercise endpoints interactively with generated OpenAPI docs.

## Interview cheat sheet
- One-liner: “A containerized FastAPI service orchestrates a deterministic assortment workflow that mirrors AURA’s Seed Plan Agent with clustering, draft generation, guardrail validation, and export.”
- Design fit: The service fits under Intelo’s agentic/orchestrator view and can publish outputs to internal adapters for ERP and reporting later.
- Trade‑offs: CSV I/O for speed of demo, greedy or heuristic seed generation to avoid heavy optimization, and deterministic steps to maximize explainability.
- Extensibility: Add conditional branches for scenario modeling, integrate OTB/PO vendor constraints, or swap CSV to ERP connectors without changing the API.
- Operability: Containerized build/run, small footprint, health endpoint, and interactive docs for handoffs and QA.

## Expected questions and model answers

- Q: How does this align with AURA’s Seed Plan Agent and its epics?
  A: It implements dynamic store clustering, automated draft seed generation, constraint-aware guardrails, and export/versioning hooks, directly mapping to modules and user stories in the PRD.

- Q: What guardrails are enforced and why?
  A: Budget caps and SKU-per-store caps are validated to ensure financial integrity and assortment manageability, matching PRD guardrails and human-in-the-loop governance.

- Q: What KPIs can this slice move?
  A: Planning time reduction, improved SKU coverage vs. targets, and better forecast alignment (as a proxy for accuracy) are impacted by automating early steps and catching violations earlier.

- Q: How would this connect to Buy Plan & PO and Pre-Allocation agents?
  A: The exported approved plan becomes the input to Buy Plan/PO for vendor/moq/lead-time constraints and then to Pre-Allocation for launch-wave optimization, per PRD handoffs.

- Q: How is explainability handled?
  A: Each recommendation is constrained by explicit rules (budget/SKU caps), and violations are surfaced with reasons so users can approve, override with rationale, or request changes.[2]

- Q: How does this fit Intelo’s high-level architecture?[1]
  A: It is an agent node exposing an API, orchestrated by a simple workflow, with outputs suitable for adapters/desks, aligning with the orchestrator-and-adapters view.

- Q: What are notable trade‑offs in the PoC?
  A: Using CSV and a linear path minimized setup time and complexity while preserving guardrails and handoffs; a future iteration could add sophisticated optimization and ERP connectors.

- Q: How does human‑in‑the‑loop apply here?
  A: The system proposes the draft plan with constraint checks, but approvals and overrides are expected before publish, per the PRD’s adoption guardrails.

- Q: How do you containerize and operate it?
  A: Build with docker build -t aura-seed-poc . and run with docker run --rm -p 8000:8000 aura-seed-poc (or docker compose up --build), then validate via /health and /docs.

- Q: How do non‑technical stakeholders use it?
  A: They can review the draft plan in familiar grid views, see rule violations clearly, and rely on exports for downstream processes without handling code or infrastructure.

## Roadmap highlights
- Scenario modeling: add what‑if overlays, multi‑metric scoring, and VM/promo/event context, as described for the Optimization Scenarios Agent.
- Buy Plan & PO: add MOQ/pack optimization, vendor allocation, cash‑flow simulation, and PO approval flows with ERP integrations.
- Pre‑Allocation: add multi‑objective launch allocation with wave scheduling and transfer suggestions for rebalancing.

## Quick reference (commands)
- Build image: docker build -t aura-seed-poc . to create the container image from the current folder.
- Run container: docker run --rm -p 8000:8000 aura-seed-poc to serve the API on port 8000.
- Compose: docker compose up --build to rebuild and start with local data/out mounts.
- curl JSON note on Windows: prefer double quotes and escape inner quotes to avoid parsing errors when posting JSON.

