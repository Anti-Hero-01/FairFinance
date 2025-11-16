"""
Prediction and loan application routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from backend.models.database import get_db, User, LoanApplication
from backend.models.mongodb import mongodb_client
from backend.schemas.application import (
    LoanApplicationCreate, LoanApplicationResponse,
    PredictionRequest, PredictionResponse
)

from backend.services.auth import get_current_active_user
from backend.services.ml_service import ml_service
from backend.services.explanation_service import explanation_service
from backend.services.encryption import encryption_service, PROTECTED_FIELDS
from backend.services.consent_service import consent_service
from backend.services.permissions import require_permission, Permission

router = APIRouter(prefix="/predict", tags=["predictions"])


@router.post("", response_model=PredictionResponse)
def predict_loan(
    request: PredictionRequest,
    current_user: User = Depends(require_permission(Permission.APPLY_FOR_LOAN)),
    db: Session = Depends(get_db)
):
    """Make loan prediction"""
    
    # Check consent
    if not consent_service.check_consent(db, current_user.id, "loan_prediction"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Consent required for loan prediction"
        )

    application_data = request.application_data.dict()

    # Make prediction
    prediction_result = ml_service.predict(application_data)

    # Generate explanation data
    explanation_data = ml_service.explain_prediction(
        application_data,
        prediction_result.get("features")
    )

    # Generate human-readable explanation text
    explanation_text = explanation_service.generate_explanation(
        prediction_result["prediction"],
        prediction_result["probability"],
        explanation_data
    )

    # Encrypt selected protected fields
    encrypted_data = encryption_service.encrypt_dict(application_data, PROTECTED_FIELDS)

    # Save application into SQL DB
    application = LoanApplication(
        user_id=current_user.id,
        age=application_data["age"],
        income=application_data["income"],
        credit_score=application_data["credit_score"],
        loan_amount=application_data["loan_amount"],
        employment_years=application_data["employment_years"],
        debt_to_income=application_data["debt_to_income"],
        credit_history_length=application_data["credit_history_length"],
        number_of_accounts=application_data["number_of_accounts"],
        defaults=application_data["defaults"],
        gender=encrypted_data.get("gender"),
        region=encrypted_data.get("region"),
        age_group=encrypted_data.get("age_group"),
        status="approved" if prediction_result["prediction"] else "denied",
        prediction=prediction_result["prediction"],
        probability=prediction_result["probability"],
        decision_reason=explanation_text,
        explanation=explanation_data
    )

    db.add(application)
    db.commit()
    db.refresh(application)

    # Log details in MongoDB
    log_data = {
        "application_id": application.id,
        "user_id": current_user.id,
        "prediction": prediction_result["prediction"],
        "probability": prediction_result["probability"],
        "model_version": "1.0",
        "features": {k: v for k, v in application_data.items() if k not in PROTECTED_FIELDS},
        "explanation": explanation_data
    }
    mongodb_client.insert_decision_log(log_data)

    # Extract top features for UI
    top_features = explanation_data.get("top_features", {})

    return PredictionResponse(
        approved=prediction_result["prediction"],
        probability=prediction_result["probability"],
        application_id=application.id,
        explanation_summary=explanation_text,
        top_features=top_features
    )


@router.get("/applications", response_model=List[LoanApplicationResponse])
def get_user_applications(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's loan applications (users see own; admins see all)"""

    if current_user.role == "user":
        applications = db.query(LoanApplication).filter(
            LoanApplication.user_id == current_user.id
        ).order_by(LoanApplication.created_at.desc()).all()
    else:
        applications = db.query(LoanApplication).order_by(
            LoanApplication.created_at.desc()
        ).all()

    return applications


@router.get("/applications/{application_id}", response_model=LoanApplicationResponse)
def get_application(
    application_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get specific application"""

    application = db.query(LoanApplication).filter(
        LoanApplication.id == application_id
    ).first()

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )

    if current_user.role == "user" and application.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You can only access your own applications"
        )

    return application
