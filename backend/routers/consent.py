"""
Consent management routes
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.models.database import get_db, User
from backend.schemas.consent import ConsentUpdate, ConsentStatus, ConsentDashboardResponse, ConsentAlert
from backend.services.auth import get_current_active_user
from backend.services.consent_service import consent_service
from backend.services.permissions import Permission, require_permission
from typing import List

router = APIRouter(prefix="/consent", tags=["consent"])

@router.get("/dashboard", response_model=ConsentDashboardResponse)
def get_consent_dashboard(
    current_user: User = Depends(require_permission(Permission.MANAGE_CONSENT)),
    db: Session = Depends(get_db)
):
    """Get user's consent dashboard (User only)"""
    consents = consent_service.get_user_consents(db, current_user.id)
    
    # Generate alerts
    alerts = []
    for consent in consents:
        if not consent.consent_given:
            alert = consent_service.generate_alert("consent_revoked", consent_changed=True)
            alerts.append(alert.message)
    
    return ConsentDashboardResponse(
        user_id=current_user.id,
        consents=consents,
        alert_messages=alerts
    )

@router.post("/update", response_model=ConsentStatus)
def update_consent(
    consent_update: ConsentUpdate,
    current_user: User = Depends(require_permission(Permission.MANAGE_CONSENT)),
    db: Session = Depends(get_db)
):
    """Update user consent (User only - can only update own consent)"""
    # Users can only update their own consent
    # This will be enforced at the service level or through user_id in request
    consent_record = consent_service.update_consent(
        db,
        current_user.id,
        consent_update.data_category,
        consent_update.consent_given
    )
    
    # Get consent config
    config = consent_service.get_consent_config()
    category_config = config.get('data_categories', {}).get(consent_update.data_category, {})
    
    return ConsentStatus(
        data_category=consent_record.data_category,
        description=category_config.get('description', ''),
        consent_given=consent_record.consent_given,
        required_for=category_config.get('required_for', []),
        last_updated=consent_record.last_updated
    )

@router.get("/alerts", response_model=List[ConsentAlert])
def get_consent_alerts(
    current_user: User = Depends(require_permission(Permission.MANAGE_CONSENT)),
    db: Session = Depends(get_db)
):
    """Get consent alerts for user (User only)"""
    consents = consent_service.get_user_consents(db, current_user.id)
    
    alerts = []
    for consent in consents:
        if not consent.consent_given:
            alert = consent_service.generate_alert("consent_revoked", consent_changed=True)
            alerts.append(alert)
    
    return alerts

@router.get("/config", response_model=dict)
def get_consent_config(
    current_user: User = Depends(require_permission(Permission.CONFIGURE_CONSENT_DEFAULTS))
):
    """Get consent configuration (Admin only)"""
    return consent_service.get_consent_config()

@router.post("/config", response_model=dict)
def update_consent_config(
    config: dict,
    current_user: User = Depends(require_permission(Permission.CONFIGURE_CONSENT_DEFAULTS)),
    db: Session = Depends(get_db)
):
    """Update consent configuration defaults (Admin only)"""
    # This would update the consent config file or database
    # For now, return the config as-is since updating file requires file system access
    # In production, this should persist to database or config management system
    return {"message": "Config update would be implemented here", "config": config}

