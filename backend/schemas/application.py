"""
Loan application schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ApplicationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    UNDER_REVIEW = "under_review"

class LoanApplicationCreate(BaseModel):
    age: int = Field(..., ge=18, le=100)
    income: float = Field(..., gt=0)
    credit_score: int = Field(..., ge=300, le=850)
    loan_amount: float = Field(..., gt=0)
    employment_years: int = Field(..., ge=0)
    debt_to_income: float = Field(..., ge=0, le=1)
    credit_history_length: int = Field(..., ge=0)
    number_of_accounts: int = Field(..., ge=0)
    defaults: int = Field(..., ge=0)
    
    # Optional protected attributes
    gender: Optional[str] = None
    region: Optional[str] = None
    age_group: Optional[str] = None

class LoanApplicationResponse(BaseModel):
    id: int
    user_id: int
    status: ApplicationStatus
    prediction: bool
    probability: float
    created_at: datetime
    decision_reason: Optional[str] = None
    explanation: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

class PredictionRequest(BaseModel):
    application_data: LoanApplicationCreate

class PredictionResponse(BaseModel):
    approved: bool
    probability: float
    application_id: int
    explanation_summary: Optional[str] = None
    top_features: Optional[Dict[str, Any]] = None

