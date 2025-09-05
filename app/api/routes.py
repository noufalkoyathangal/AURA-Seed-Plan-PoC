from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import List, Dict, Optional
import asyncio
from datetime import datetime, timedelta
import uuid
import logging

from app.models.store import StoreClusterRequest, ClusterResult
from app.models.sku import (
    AutoSeedPlanRequest, 
    SeedPlanResult,
    SeedPlanRequest,
    AutoSeedPlanResult,
    PlanningConstraints
)
from app.models.planning_line import ValidationRequest, ValidationResult
from app.models.user import User
from app.services.clustering import ClusteringService
from app.services.seed import SeedGeneratorService
from app.services.constraints import ConstraintsService
from app.auth.rbac import require_permission

router = APIRouter(prefix="/api", tags=["seed-plan"])
logger = logging.getLogger(__name__)

# Initialize services
clustering_service = ClusteringService()
seed_service = SeedGeneratorService()
constraints_service = ConstraintsService()

@router.post("/seed/cluster", response_model=ClusterResult)
async def cluster_stores(
    request: StoreClusterRequest,
    user=Depends(require_permission("cluster:create"))
):
    """
    Cluster stores using ML algorithms (K-means, Fuzzy C-means)
    """
    try:
        logger.info(f"User {user['id']} requested store clustering")
        result = await clustering_service.cluster_stores(
            stores_csv=request.stores_csv,
            features=request.features,
            algorithm=request.algorithm,
            n_clusters=request.n_clusters
        )
        logger.info(f"Clustering completed with {len(result.cluster_map)} stores")
        return result
    except ValueError as e:
        logger.warning(f"Invalid clustering request: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid request: {str(e)}")
    except Exception as e:
        logger.error(f"Clustering failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Clustering service unavailable")


@router.post("/seed/generate", response_model=SeedPlanResult)
async def generate_seed_plan(
    request: SeedPlanRequest,
    user=Depends(require_permission("seed:create"))
):
    """
    Generate draft seed plan with forecasting and constraints
    """
    try:
        logger.info(f"User {user['id']} generating seed plan")
        result = await seed_service.generate_plan(
            skus_csv=request.skus_csv,
            cluster_map=request.cluster_map,
            constraints=request.constraints
        )
        logger.info(f"Seed plan generated: {result.plan_id}")
        return result
    except ValueError as e:
        logger.warning(f"Invalid seed plan request: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except Exception as e:
        logger.error(f"Seed plan generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Seed generation service unavailable")


@router.post("/seed/validate", response_model=ValidationResult)
async def validate_plan(
    request: ValidationRequest,
    user=Depends(require_permission("seed:validate"))
):
    """
    Validate plan against business rules and guardrails
    """
    try:
        logger.info(f"User {user['id']} validating plan with {len(request.lines)} lines")
        result = await constraints_service.validate_plan(
            lines=request.lines,
            rules=request.rules
        )
        logger.info(f"Validation completed: {len(result.violations)} violations found")
        return result
    except Exception as e:
        logger.error(f"Plan validation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Validation service unavailable")


@router.post("/seed/approve/{plan_id}")
async def approve_plan(
    plan_id: str,
    user=Depends(require_permission("seed:approve"))
):
    """
    Approve seed plan for publishing
    """
    try:
        logger.info(f"User {user['id']} approving plan {plan_id}")
        # TODO: Implement approval workflow logic
        # - Update plan status in database
        # - Send notifications to stakeholders
        # - Create audit trail entry
        
        return {
            "status": "approved", 
            "plan_id": plan_id,
            "approved_by": user['id'],
            "approved_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Plan approval failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Approval service unavailable")


@router.post("/seed/auto", response_model=AutoSeedPlanResult)
async def auto_workflow(
    request: AutoSeedPlanRequest,
    background_tasks: BackgroundTasks,
    user=Depends(require_permission("seed:execute"))
):
    """
    Execute complete workflow: cluster → generate → validate → export
    """
    try:
        logger.info(f"User {user['id']} starting auto workflow")
        
        # Generate cluster_map if not provided
        if request.cluster_map is None:
            logger.info("Auto-clustering stores")
            cluster_result = await clustering_service.cluster_stores(
                stores_csv="data/stores.csv",
                features=request.clustering_features,
                algorithm=request.clustering_algorithm,
                n_clusters=request.n_clusters
            )
            cluster_map = cluster_result.cluster_map
        else:
            cluster_map = request.cluster_map
        
        # Generate constraints if not provided
        constraints = request.custom_constraints or {
            "budget": request.budget,
            "max_skus_per_store": request.max_skus_per_store,
            "min_skus_per_store": 1,
            "fixture_constraints": {}
        }
        
        # Create full seed plan request
        full_request = SeedPlanRequest(
            skus_csv=request.skus_csv,
            cluster_map=cluster_map,
            constraints=PlanningConstraints(**constraints),
            use_forecasting=request.use_forecasting
        )
        
        # Execute workflow in background
        task_id = str(uuid.uuid4())
        background_tasks.add_task(
            execute_full_workflow, 
            full_request, 
            user["id"],  # ✅ Fixed: use dictionary access
            task_id
        )
        
        logger.info(f"Background workflow {task_id} started")
        
        return AutoSeedPlanResult(
            task_id=task_id,
            status="started",
            estimated_completion=(datetime.utcnow() + timedelta(minutes=5)).isoformat()
        )
    except Exception as e:
        logger.error(f"Auto workflow failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Auto workflow failed: {str(e)}")


@router.get("/seed/auto/status/{task_id}")
async def get_workflow_status(
    task_id: str,
    user=Depends(require_permission("seed:view"))
):
    """
    Get status of background workflow execution
    """
    try:
        # TODO: Implement task status tracking
        # - Check Redis/database for task status
        # - Return progress, results, or error details
        
        return {
            "task_id": task_id,
            "status": "running",  # "running", "completed", "failed"
            "progress": 75,
            "message": "Generating seed plan...",
            "result": None,
            "error": None
        }
    except Exception as e:
        logger.error(f"Status check failed for task {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Status service unavailable")


async def execute_full_workflow(request: SeedPlanRequest, user_id: str, task_id: str):
    """
    Background task for complete workflow execution
    """
    try:
        logger.info(f"Executing workflow {task_id} for user {user_id}")
        
        # Step 1: Generate seed plan
        logger.info(f"Step 1/4: Generating seed plan for task {task_id}")
        seed_result = await seed_service.generate_plan(
            skus_csv=request.skus_csv,
            cluster_map=request.cluster_map,
            constraints=request.constraints
        )
        
        # Step 2: Validate generated plan
        logger.info(f"Step 2/4: Validating plan for task {task_id}")
        validation_request = ValidationRequest(
            lines=[{
                "sku": line.sku_id, 
                "store": line.store_id, 
                "qty": line.qty,
                "cost": getattr(line, 'cost', 0)
            } for line in seed_result.lines],
            rules={
                "budget": request.constraints.budget,
                "max_skus_per_store": request.constraints.max_skus_per_store
            }
        )
        
        validation_result = await constraints_service.validate_plan(
            lines=validation_request.lines,
            rules=validation_request.rules
        )
        
        # Step 3: Handle validation results
        if validation_result.is_valid:
            logger.info(f"Step 3/4: Plan validated successfully for task {task_id}")
            # Auto-approve valid plans
            status = "auto_approved"
        else:
            logger.warning(f"Plan validation failed for task {task_id}: {len(validation_result.violations)} violations")
            status = "requires_manual_review"
        
        # Step 4: Export results
        logger.info(f"Step 4/4: Exporting results for task {task_id}")
        # TODO: Implement export functionality
        export_path = f"exports/seed_plan_{task_id}.csv"
        
        # Final result
        final_result = {
            "plan_id": seed_result.plan_id,
            "validation_status": status,
            "violations": len(validation_result.violations),
            "export_path": export_path,
            "total_cost": seed_result.total_cost,
            "sku_count": len(seed_result.lines),
            "completed_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Workflow {task_id} completed successfully")
        # TODO: Update task status in database/cache
        
    except Exception as e:
        logger.error(f"Workflow {task_id} failed: {str(e)}")
        # TODO: Update task status with error
        raise
