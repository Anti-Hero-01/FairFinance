"""
Explanation schemas for SHAP and ethical twin
"""

from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class FeatureContribution(BaseModel):
    feature: str
    value: float
    contribution: float

class ExplanationResponse(BaseModel):
    application_id: int
    prediction: bool
    probability: float
    top_positive_features: List[FeatureContribution]
    top_negative_features: List[FeatureContribution]
    shap_values: Optional[Dict[str, float]] = None
    ethical_twin_explanation: Optional[Dict[str, Any]] = None
    explanation_text: str

class ProfileExplanationRequest(BaseModel):
    user_id: int

class ProfileExplanationResponse(BaseModel):
    user_id: int
    risk_category: str
    top_global_features: List[FeatureContribution]
    improvement_suggestions: List[str]
    explanation_text: str

