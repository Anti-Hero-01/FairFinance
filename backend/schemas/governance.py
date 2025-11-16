"""
Governance and audit schemas
"""

from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from datetime import datetime

class DecisionLogEntry(BaseModel):
    application_id: int
    user_id: int
    prediction: bool
    probability: float
    model_version: str
    timestamp: datetime
    features: Dict[str, Any]
    explanation: Optional[Dict[str, Any]] = None
    admin_override: bool = False
    override_reason: Optional[str] = None

class FairnessMetric(BaseModel):
    metric_name: str
    value: float
    threshold: float
    status: str  # "pass" or "violation"
    attribute: str

class FairnessReportResponse(BaseModel):
    report_id: str
    generated_at: datetime
    metrics: List[FairnessMetric]
    violations: List[Dict[str, Any]]
    recommendations: List[str]
    report_path: Optional[str] = None

class AdminOverrideRequest(BaseModel):
    application_id: int
    new_decision: bool
    reason: str

class AuditTrailEntry(BaseModel):
    action: str
    user_id: int
    user_role: str
    timestamp: datetime
    details: Dict[str, Any]

