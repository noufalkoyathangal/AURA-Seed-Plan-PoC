import pandas as pd
import numpy as np
from typing import Dict, List
from decimal import Decimal
import asyncio
from prophet import Prophet
from datetime import datetime, timedelta

from app.models.sku import SeedPlanResult, PlanningConstraints

class SeedGeneratorService:
    """Advanced seed plan generator with forecasting"""
    
    async def generate_plan(
        self,
        skus_csv: str,
        cluster_map: Dict[str, int],
        constraints: PlanningConstraints,
        use_forecasting: bool = True
    ) -> SeedPlanResult:
        """
        Generate seed plan with constraint adherence and forecasting
        """
        # Load SKU data
        skus_df = pd.read_csv(skus_csv)
        
        # Generate demand forecasts if enabled
        demand_forecasts = {}
        if use_forecasting:
            demand_forecasts = await self._generate_forecasts(skus_df, cluster_map)
        
        # Generate initial plan
        plan_lines = await self._generate_plan_lines(
            skus_df, cluster_map, constraints, demand_forecasts
        )
        
        # Calculate confidence scores
        confidence_scores = await self._calculate_confidence_scores(
            plan_lines, demand_forecasts
        )
        
        # Calculate statistics
        total_cost = sum(Decimal(str(line['cost'])) for line in plan_lines)
        coverage_stats = await self._calculate_coverage_stats(
            plan_lines, cluster_map, constraints
        )
        
        plan_id = f"seed_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        return SeedPlanResult(
            plan_id=plan_id,
            lines=plan_lines,
            total_cost=total_cost,
            coverage_stats=coverage_stats,
            confidence_scores=confidence_scores
        )
    
    async def _generate_forecasts(
        self, 
        skus_df: pd.DataFrame, 
        cluster_map: Dict[str, int]
    ) -> Dict:
        """Generate demand forecasts using Prophet"""
        forecasts = {}
        
        # Mock forecast generation (in real implementation, use historical sales data)
        for _, sku in skus_df.iterrows():
            sku_id = sku['sku_id']
            
            # Create mock historical data
            dates = pd.date_range(
                start=datetime.now() - timedelta(days=365),
                end=datetime.now(),
                freq='D'
            )
            
            # Generate synthetic demand pattern
            base_demand = np.random.poisson(10, len(dates))
            seasonal_pattern = 5 * np.sin(2 * np.pi * np.arange(len(dates)) / 365)
            demand = base_demand + seasonal_pattern + np.random.normal(0, 2, len(dates))
            demand = np.maximum(demand, 0)  # Ensure non-negative
            
            forecasts[sku_id] = {
                "forecast_demand": float(np.mean(demand[-30:])),  # Last 30 days average
                "confidence": 0.8,  # Mock confidence
                "trend": "stable"
            }
        
        return forecasts
    
    async def _generate_plan_lines(
        self,
        skus_df: pd.DataFrame,
        cluster_map: Dict[str, int],
        constraints: PlanningConstraints,
        demand_forecasts: Dict
    ) -> List[Dict]:
        """Generate planning lines with greedy allocation"""
        lines = []
        remaining_budget = float(constraints.budget)
        
        # Sort SKUs by forecasted demand (descending)
        sku_priorities = []
        for _, sku in skus_df.iterrows():
            forecast = demand_forecasts.get(sku['sku_id'], {})
            priority = forecast.get('forecast_demand', 5.0)  # Default demand
            sku_priorities.append((priority, sku))
        
        sku_priorities.sort(key=lambda x: x[0], reverse=True)
        
        # Allocate SKUs to stores within constraints
        store_sku_counts = {store: 0 for store in cluster_map.keys()}
        
        for priority, sku in sku_priorities:
            sku_cost = float(sku['cost'])
            
            if remaining_budget < sku_cost:
                continue
            
            # Find stores in same cluster that can accommodate this SKU
            eligible_stores = [
                store for store, count in store_sku_counts.items()
                if count < constraints.max_skus_per_store
            ]
            
            if not eligible_stores:
                continue
            
            # Allocate to stores (simplified - could be more sophisticated)
            for store in eligible_stores[:3]:  # Limit to 3 stores per SKU
                if remaining_budget >= sku_cost:
                    quantity = max(1, int(priority / 2))  # Base quantity on demand
                    line_cost = sku_cost * quantity
                    
                    if remaining_budget >= line_cost:
                        lines.append({
                            "sku": sku['sku_id'],
                            "store": store,
                            "cluster": cluster_map[store],
                            "quantity": quantity,
                            "unit_cost": sku_cost,
                            "cost": line_cost,
                            "forecast_demand": priority
                        })
                        
                        remaining_budget -= line_cost
                        store_sku_counts[store] += 1
        
        return lines
    
    async def _calculate_confidence_scores(
        self, 
        plan_lines: List[Dict], 
        demand_forecasts: Dict
    ) -> Dict:
        """Calculate confidence scores for each planning line"""
        confidence_scores = {}
        
        for line in plan_lines:
            sku_id = line['sku']
            forecast = demand_forecasts.get(sku_id, {})
            
            # Base confidence on forecast accuracy and demand stability
            base_confidence = forecast.get('confidence', 0.5)
            demand_ratio = line['quantity'] / max(line['forecast_demand'], 1)
            
            # Penalize over-allocation
            if demand_ratio > 1.5:
                confidence = base_confidence * 0.7
            elif demand_ratio > 1.0:
                confidence = base_confidence * 0.9
            else:
                confidence = base_confidence
            
            line_key = f"{line['sku']}_{line['store']}"
            confidence_scores[line_key] = min(confidence, 1.0)
        
        return confidence_scores
    
    async def _calculate_coverage_stats(
        self,
        plan_lines: List[Dict],
        cluster_map: Dict[str, int],
        constraints: PlanningConstraints
    ) -> Dict:
        """Calculate coverage and utilization statistics"""
        total_stores = len(cluster_map)
        stores_with_skus = len(set(line['store'] for line in plan_lines))
        total_skus = len(set(line['sku'] for line in plan_lines))
        
        budget_utilization = sum(line['cost'] for line in plan_lines) / float(constraints.budget)
        
        return {
            "store_coverage": stores_with_skus / total_stores,
            "total_skus_planned": total_skus,
            "total_lines": len(plan_lines),
            "budget_utilization": budget_utilization,
            "avg_skus_per_store": total_skus / max(stores_with_skus, 1)
        }
