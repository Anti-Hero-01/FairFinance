"""
Consent management schemas
"""

from pydantic import BaseModel
from typing import Dict, Optional, List
from datetime import datetime

class ConsentUpdate(BaseModel):
    data_category: str
    consent_given: bool

class ConsentStatus(BaseModel):
    data_category: str
    description: str
    consent_given: bool
    required_for: List[str]
    last_updated: datetime

class ConsentDashboardResponse(BaseModel):
    user_id: int
    consents: List[ConsentStatus]
    alert_messages: List[str]

class ConsentAlert(BaseModel):
    message: str
    timestamp: datetime
    action: str

