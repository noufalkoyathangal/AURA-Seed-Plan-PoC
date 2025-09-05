from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from decimal import Decimal

class ValidationRequest(BaseModel):
    lines: List[Dict] = Field(..., description="Planning lines to validate")
    rules: Dict = Field(..., description="Business rules to apply")

class Violation(BaseModel):
    type: str = Field(..., description="Type of violation")
    message: str = Field(..., description="Violation message")
    severity: str = Field(..., description="Severity level")
    suggestion: str = Field(..., description="Suggested fix")

class ValidationResult(BaseModel):
    is_valid: bool = Field(..., description="Whether plan is valid")
    violations: List[Violation] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    summary: Dict = Field(..., description="Validation summary")
