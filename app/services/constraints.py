from typing import List, Dict
from decimal import Decimal
import asyncio

from app.models.planning_line import ValidationResult, Violation

class ConstraintsService:
    """Business rules and constraints validation service"""
    
    async def validate_plan(
        self,
        lines: List[Dict],
        rules: Dict
    ) -> ValidationResult:
        """
        Validate planning lines against business rules
        """
        violations = []
        suggestions = []
        
        # Budget validation
        budget_violations = await self._validate_budget(lines, rules)
        violations.extend(budget_violations)
        
        # SKU count validation
        sku_violations = await self._validate_sku_limits(lines, rules)
        violations.extend(sku_violations)
        
        # Fixture capacity validation
        fixture_violations = await self._validate_fixture_capacity(lines, rules)
        violations.extend(fixture_violations)
        
        # Generate suggestions for violations
        if violations:
            suggestions = await self._generate_suggestions(violations, lines)
        
        # Determine overall validation status
        critical_violations = [v for v in violations if v.severity == "critical"]
        is_valid = len(critical_violations) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            violations=violations,
            suggestions=suggestions,
            summary={
                "total_violations": len(violations),
                "critical_violations": len(critical_violations),
                "warning_violations": len(violations) - len(critical_violations)
            }
        )
    
    async def _validate_budget(self, lines: List[Dict], rules: Dict) -> List[Violation]:
        """Validate budget constraints"""
        violations = []
        max_budget = rules.get('budget', float('inf'))
        
        total_cost = sum(Decimal(str(line['cost'])) for line in lines)
        
        if total_cost > max_budget:
            violations.append(Violation(
                type="budget_exceeded",
                message=f"Total cost ${total_cost} exceeds budget ${max_budget}",
                severity="critical",
                suggestion=f"Reduce allocation by ${total_cost - max_budget}"
            ))
        
        return violations
    
    async def _validate_sku_limits(self, lines: List[Dict], rules: Dict) -> List[Violation]:
        """Validate SKU count limits per store"""
        violations = []
        max_skus = rules.get('max_skus_per_store', float('inf'))
        min_skus = rules.get('min_skus_per_store', 0)
        
        # Count SKUs per store
        store_sku_counts = {}
        for line in lines:
            store = line['store']
            if store not in store_sku_counts:
                store_sku_counts[store] = set()
            store_sku_counts[store].add(line['sku'])
        
        for store, skus in store_sku_counts.items():
            sku_count = len(skus)
            
            if sku_count > max_skus:
                violations.append(Violation(
                    type="sku_limit_exceeded",
                    message=f"Store {store} has {sku_count} SKUs, exceeds limit of {max_skus}",
                    severity="critical",
                    suggestion=f"Remove {sku_count - max_skus} SKUs from store {store}"
                ))
            
            if sku_count < min_skus:
                violations.append(Violation(
                    type="sku_minimum_not_met",
                    message=f"Store {store} has {sku_count} SKUs, below minimum of {min_skus}",
                    severity="warning",
                    suggestion=f"Add {min_skus - sku_count} SKUs to store {store}"
                ))
        
        return violations
    
    async def _validate_fixture_capacity(self, lines: List[Dict], rules: Dict) -> List[Violation]:
        """Validate fixture and display capacity constraints"""
        violations = []
        fixture_rules = rules.get('fixture_constraints', {})
        
        if not fixture_rules:
            return violations
        
        # Group by store and calculate space usage
        store_space_usage = {}
        for line in lines:
            store = line['store']
            # Mock space calculation (would use actual SKU dimensions)
            space_used = line['quantity'] * 0.1  # Assume 0.1 sq ft per unit
            
            if store not in store_space_usage:
                store_space_usage[store] = 0
            store_space_usage[store] += space_used
        
        # Check against capacity limits
        for store, space_used in store_space_usage.items():
            max_space = fixture_rules.get('max_space_per_store', float('inf'))
            
            if space_used > max_space:
                violations.append(Violation(
                    type="fixture_capacity_exceeded",
                    message=f"Store {store} uses {space_used:.1f} sq ft, exceeds {max_space} sq ft",
                    severity="warning",
                    suggestion=f"Reduce quantities to free up {space_used - max_space:.1f} sq ft"
                ))
        
        return violations
    
    async def _generate_suggestions(
        self, 
        violations: List[Violation], 
        lines: List[Dict]
    ) -> List[str]:
        """Generate actionable suggestions based on violations"""
        suggestions = []
        
        # Extract existing suggestions from violations
        for violation in violations:
            if violation.suggestion:
                suggestions.append(violation.suggestion)
        
        # Add general optimization suggestions
        if any(v.type == "budget_exceeded" for v in violations):
            suggestions.append("Consider prioritizing higher-forecasted SKUs")
            suggestions.append("Review and reduce quantities for low-confidence recommendations")
        
        if any(v.type.startswith("sku_") for v in violations):
            suggestions.append("Rebalance SKU distribution across stores")
            suggestions.append("Consider merging similar clusters to simplify assortment")
        
        return list(set(suggestions))  # Remove duplicates
