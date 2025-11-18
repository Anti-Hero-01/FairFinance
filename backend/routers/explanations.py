"""
Explanation routes for SHAP and ethical twin
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.models.database import get_db, User, LoanApplication
from backend.schemas.explanation import ExplanationResponse, ProfileExplanationRequest, ProfileExplanationResponse
from backend.services.auth import get_current_active_user
from backend.services.ml_service import ml_service
from backend.services.explanation_service import explanation_service
from backend.services.consent_service import consent_service
from backend.services.permissions import Permission, require_own_resource_or_permission, require_permission
from numbers import Number

router = APIRouter(prefix="/explain", tags=["explanations"])

@router.get("/{application_id}", response_model=ExplanationResponse)
def explain_application(
    application_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get explanation for a specific application (users see own SHAP, admins/auditors see all)"""
    application = db.query(LoanApplication).filter(
        LoanApplication.id == application_id
    ).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Permission check: Users can only view their own SHAP explanations
    # Admins and auditors can view all explanations
    if current_user.role == "user":
        # Check consent for users
        if not consent_service.check_consent(db, current_user.id, "loan_prediction"):
            raise HTTPException(status_code=403, detail="Consent required")
        # Users can only access their own explanations
        if application.user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Access denied: You can only view your own SHAP explanations"
            )
    else:
        # Admins and auditors have VIEW_ALL_EXPLANATIONS permission
        from backend.services.permissions import has_permission
        if not has_permission(current_user, Permission.VIEW_ALL_EXPLANATIONS):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Get explanation from stored data or regenerate
    explanation_data = application.explanation
    if explanation_data is None:
        explanation_data = {}
    if not isinstance(explanation_data, dict):
        explanation_data = {}
    
    # Format response - handle None case
    shap_exp = explanation_data.get('shap_explanation')
    if shap_exp is None or not isinstance(shap_exp, dict):
        shap_exp = {}
    
    top_pos = shap_exp.get('top_positive', []) if isinstance(shap_exp, dict) else []
    top_neg = shap_exp.get('top_negative', []) if isinstance(shap_exp, dict) else []
    
    # Ensure top_pos and top_neg are lists
    if not isinstance(top_pos, list):
        top_pos = []
    if not isinstance(top_neg, list):
        top_neg = []
    
    from backend.schemas.explanation import FeatureContribution
    
    top_positive_features = [
        FeatureContribution(
            feature=f.get('feature', ''),
            value=(f.get('value') if isinstance(f.get('value'), Number) else 0.0),
            contribution=(float(f.get('contribution')) if isinstance(f.get('contribution'), Number) else 0.0)
        ) for f in top_pos
    ]
    
    top_negative_features = [
        FeatureContribution(
            feature=f.get('feature', ''),
            value=(f.get('value') if isinstance(f.get('value'), Number) else 0.0),
            contribution=(float(f.get('contribution')) if isinstance(f.get('contribution'), Number) else 0.0)
        ) for f in top_neg
    ]
    
    # Build shap_values dict safely
    shap_values = {}
    for f in top_pos + top_neg:
        if isinstance(f, dict) and 'feature' in f:
            contrib = f.get('contribution')
            shap_values[f['feature']] = float(contrib) if isinstance(contrib, Number) else 0.0
    
    return ExplanationResponse(
        application_id=application.id,
        prediction=application.prediction if application.prediction is not None else False,
        probability=application.probability if application.probability is not None else 0.0,
        top_positive_features=top_positive_features,
        top_negative_features=top_negative_features,
        shap_values=shap_values,
        ethical_twin_explanation=explanation_data.get('ethical_twin_explanation') if isinstance(explanation_data, dict) else None,
        explanation_text=application.decision_reason or "No explanation available"
    )

@router.post("/profile", response_model=ProfileExplanationResponse)
def explain_profile(
    request: ProfileExplanationRequest,
    current_user: User = Depends(require_permission(Permission.VIEW_PROFILE_EXPLANATION)),
    db: Session = Depends(get_db)
):
    """Explain user's financial profile (users can only view their own)"""
    # Users can only view their own profile explanations
    if request.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Access denied: You can only view your own profile explanation"
        )
    
    # Check consent
    if not consent_service.check_consent(db, current_user.id, "profile_explanation"):
        raise HTTPException(status_code=403, detail="Consent required")
    
    # Get user's applications
    applications = db.query(LoanApplication).filter(
        LoanApplication.user_id == request.user_id
    ).all()
    
    # Convert to dict format
    apps_data = []
    for app in applications:
        apps_data.append({
            'prediction': app.prediction,
            'probability': app.probability,
            'explanation': app.explanation or {}
        })
    
    # Generate profile explanation
    profile_exp = explanation_service.generate_profile_explanation(apps_data)
    
    from backend.schemas.explanation import FeatureContribution
    
    top_global_features = [
        FeatureContribution(
            feature=f.get('feature', ''),
            value=0.0,
            contribution=(f.get('contribution') if isinstance(f.get('contribution'), Number) else f.get('importance', 0.0))
        ) for f in profile_exp.get('top_global_features', [])
    ]
    
    return ProfileExplanationResponse(
        user_id=request.user_id,
        risk_category=profile_exp.get('risk_category', 'unknown'),
        top_global_features=top_global_features,
        improvement_suggestions=profile_exp.get('improvement_suggestions', []),
        explanation_text=profile_exp.get('explanation_text', 'Profile analysis completed.')
    )

@router.get("/all", response_model=List[ExplanationResponse])
def get_all_explanations(
    current_user: User = Depends(require_permission(Permission.VIEW_ALL_EXPLANATIONS)),
    db: Session = Depends(get_db),
    limit: int = 100
):
    """Get all explanations (Auditor/Admin only)"""
    from backend.services.permissions import has_permission
    if not has_permission(current_user, Permission.VIEW_ALL_EXPLANATIONS):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Get all applications with explanations
    applications = db.query(LoanApplication).filter(
        LoanApplication.explanation.isnot(None)
    ).order_by(LoanApplication.created_at.desc()).limit(limit).all()
    
    explanations = []
    for application in applications:
        explanation_data = application.explanation
        if explanation_data is None:
            explanation_data = {}
        if not isinstance(explanation_data, dict):
            explanation_data = {}
        
        shap_exp = explanation_data.get('shap_explanation')
        if shap_exp is None or not isinstance(shap_exp, dict):
            shap_exp = {}
        
        top_pos = shap_exp.get('top_positive', []) if isinstance(shap_exp, dict) else []
        top_neg = shap_exp.get('top_negative', []) if isinstance(shap_exp, dict) else []
        
        # Ensure top_pos and top_neg are lists
        if not isinstance(top_pos, list):
            top_pos = []
        if not isinstance(top_neg, list):
            top_neg = []
        
        from backend.schemas.explanation import FeatureContribution
        
        top_positive_features = [
            FeatureContribution(
                feature=f.get('feature', ''),
                value=f.get('value', 0),
                contribution=f.get('contribution', 0)
            ) for f in top_pos
        ]
        
        top_negative_features = [
            FeatureContribution(
                feature=f.get('feature', ''),
                value=f.get('value', 0),
                contribution=f.get('contribution', 0)
            ) for f in top_neg
        ]
        
        # Build shap_values dict safely
        shap_values = {}
        for f in top_pos + top_neg:
            if isinstance(f, dict) and 'feature' in f:
                shap_values[f['feature']] = f.get('contribution', 0)
        
        explanations.append(ExplanationResponse(
            application_id=application.id,
            prediction=application.prediction if application.prediction is not None else False,
            probability=application.probability if application.probability is not None else 0.0,
            top_positive_features=top_positive_features,
            top_negative_features=top_negative_features,
            shap_values=shap_values,
            ethical_twin_explanation=explanation_data.get('ethical_twin_explanation') if isinstance(explanation_data, dict) else None,
            explanation_text=application.decision_reason or "No explanation available"
        ))
    
    return explanations

