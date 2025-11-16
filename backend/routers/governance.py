"""
Governance and audit routes
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from backend.models.database import get_db, User, LoanApplication
from backend.models.mongodb import mongodb_client
from backend.schemas.governance import (
    DecisionLogEntry, FairnessReportResponse, AdminOverrideRequest, AuditTrailEntry
)
from backend.services.auth import get_current_active_user
from backend.services.permissions import (
    Permission, require_permission, require_any_permission,
    require_own_resource_or_permission, has_permission
)
from backend.services.fairness_service import fairness_service

router = APIRouter(prefix="/governance", tags=["governance"])

@router.get("/decision-log/{user_id}", response_model=List[DecisionLogEntry])
def get_decision_log(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get decision log for a user (Own for User, All for Auditor/Admin)"""
    # Users can only view their own logs
    if current_user.role == "user":
        if user_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Access denied: You can only view your own decision logs"
            )
        # Check permission
        if not has_permission(current_user, Permission.VIEW_OWN_LOGS):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        # For users, always use their own ID
        actual_user_id = current_user.id
    else:
        # Admins and auditors can view all logs (can view any user_id)
        if not has_permission(current_user, Permission.VIEW_ALL_LOGS):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        # Use provided user_id
        actual_user_id = user_id
    
    # Get logs from MongoDB
    logs = mongodb_client.get_decision_logs(user_id=actual_user_id, limit=100)
    
    # Convert to response format
    decision_logs = []
    for log in logs:
        decision_logs.append(DecisionLogEntry(
            application_id=log.get('application_id'),
            user_id=log.get('user_id'),
            prediction=log.get('prediction'),
            probability=log.get('probability'),
            model_version=log.get('model_version', '1.0'),
            timestamp=log.get('timestamp'),
            features=log.get('features', {}),
            explanation=log.get('explanation'),
            admin_override=log.get('admin_override', False),
            override_reason=log.get('override_reason')
        ))
    
    return decision_logs

@router.get("/fairness-report", response_model=FairnessReportResponse)
def get_fairness_report(
    current_user: User = Depends(require_permission(Permission.VIEW_FAIRNESS_METRICS)),
    db: Session = Depends(get_db)
):
    """Get fairness metrics report (Auditor/Admin only)"""
    report = fairness_service.generate_fairness_report(db)
    
    if 'error' in report:
        raise HTTPException(status_code=400, detail=report['error'])
    
    # Format violations as metrics
    from backend.schemas.governance import FairnessMetric
    
    metrics = []
    violations_list = []
    
    for attr, attr_metrics in report.get('metrics', {}).items():
        if 'demographic_parity_difference' in attr_metrics:
            dpd = attr_metrics['demographic_parity_difference']
            threshold = 0.1
            metrics.append(FairnessMetric(
                metric_name='demographic_parity_difference',
                value=dpd,
                threshold=threshold,
                status='violation' if dpd > threshold else 'pass',
                attribute=attr
            ))
        
        if 'equal_opportunity_difference' in attr_metrics:
            eod = attr_metrics['equal_opportunity_difference']
            threshold = 0.1
            metrics.append(FairnessMetric(
                metric_name='equal_opportunity_difference',
                value=eod,
                threshold=threshold,
                status='violation' if eod > threshold else 'pass',
                attribute=attr
            ))
    
    violations_list = report.get('violations', [])
    
    recommendations = [
        "Review model training data for representation balance",
        "Consider post-processing techniques to mitigate bias",
        "Monitor fairness metrics in production",
        "Implement bias mitigation strategies if violations persist"
    ]
    
    return FairnessReportResponse(
        report_id=report.get('report_id', ''),
        generated_at=report.get('generated_at'),
        metrics=metrics,
        violations=violations_list,
        recommendations=recommendations,
        report_path=report.get('report_path')
    )

@router.post("/admin/override", response_model=DecisionLogEntry)
def admin_override(
    override_request: AdminOverrideRequest,
    current_user: User = Depends(require_any_permission([
        Permission.OVERRIDE_DECISION_RECOMMEND,
        Permission.OVERRIDE_DECISION_APPROVE
    ])),
    db: Session = Depends(get_db)
):
    """Override loan decision (Recommend for Auditor, Approve for Admin)"""
    # Check if user has approve permission (admin) or recommend permission (auditor)
    is_admin = has_permission(current_user, Permission.OVERRIDE_DECISION_APPROVE)
    is_auditor = has_permission(current_user, Permission.OVERRIDE_DECISION_RECOMMEND)
    
    if not (is_admin or is_auditor):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Auditors can only recommend, admins can approve
    action_type = "approved" if is_admin else "recommended"
    application = db.query(LoanApplication).filter(
        LoanApplication.id == override_request.application_id
    ).first()
    
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    
    # Update application
    # Only admins can actually override, auditors can only recommend
    if is_admin:
        application.status = "approved" if override_request.new_decision else "denied"
        application.prediction = override_request.new_decision
        application.admin_override = True
        application.override_reason = override_request.reason
        db.commit()
        db.refresh(application)
    else:
        # Auditor recommendation - don't actually override, just log recommendation
        # In a real system, this would create a recommendation that needs admin approval
        pass
    
    # Log to audit trail
    audit_data = {
        'action': 'admin_override' if is_admin else 'auditor_recommendation',
        'user_id': current_user.id,
        'user_role': current_user.role,
        'application_id': override_request.application_id,
        'old_decision': application.prediction,
        'new_decision': override_request.new_decision,
        'reason': override_request.reason,
        'action_type': action_type
    }
    mongodb_client.insert_audit_trail(audit_data)
    
    # Update decision log
    log_data = {
        'application_id': application.id,
        'user_id': application.user_id,
        'prediction': override_request.new_decision,
        'probability': application.probability or 0.5,
        'model_version': '1.0',
        'features': {},
        'admin_override': True,
        'override_reason': override_request.reason
    }
    mongodb_client.insert_decision_log(log_data)
    
    return DecisionLogEntry(
        application_id=application.id,
        user_id=application.user_id,
        prediction=application.prediction,
        probability=application.probability or 0.5,
        model_version='1.0',
        timestamp=application.updated_at,
        features={},
        admin_override=True,
        override_reason=override_request.reason
    )

@router.get("/audit-trail", response_model=List[AuditTrailEntry])
def get_audit_trail(
    current_user: User = Depends(require_permission(Permission.VIEW_ALL_LOGS)),
    limit: int = 100
):
    """Get audit trail (Auditor/Admin only)"""
    trails = mongodb_client.get_audit_trails(limit=limit)
    
    audit_entries = []
    for trail in trails:
        audit_entries.append(AuditTrailEntry(
            action=trail.get('action', ''),
            user_id=trail.get('user_id'),
            user_role=trail.get('user_role', ''),
            timestamp=trail.get('timestamp'),
            details={k: v for k, v in trail.items() if k not in ['_id', 'action', 'user_id', 'user_role', 'timestamp']}
        ))
    
    return audit_entries

@router.get("/export-logs")
def export_logs(
    current_user: User = Depends(require_any_permission([
        Permission.EXPORT_LOGS_LIMITED,
        Permission.EXPORT_LOGS_FULL
    ])),
    user_id: Optional[int] = None,
    format: str = "json"
):
    """Export decision logs (Limited for Auditor, Full for Admin)"""
    from backend.services.permissions import has_permission
    
    has_full_export = has_permission(current_user, Permission.EXPORT_LOGS_FULL)
    
    # Auditors can only export limited data (no protected fields)
    # Admins can export full data including all fields
    if has_full_export:
        # Admin: export all logs
        logs = mongodb_client.get_decision_logs(user_id=user_id, limit=10000)
    else:
        # Auditor: export limited logs (sanitized)
        logs = mongodb_client.get_decision_logs(user_id=user_id, limit=1000)
        # Remove sensitive information for auditors
        for log in logs:
            log.pop('features', None)
    
    if format == "csv":
        # Convert to CSV format
        import csv
        from io import StringIO
        output = StringIO()
        if logs:
            # Flatten nested structures for CSV
            flattened_logs = []
            for log in logs:
                flat_log = {
                    'application_id': log.get('application_id', ''),
                    'user_id': log.get('user_id', ''),
                    'prediction': log.get('prediction', ''),
                    'probability': log.get('probability', ''),
                    'model_version': log.get('model_version', ''),
                    'timestamp': str(log.get('timestamp', '')),
                    'admin_override': log.get('admin_override', False),
                }
                if has_full_export:
                    # Include features for admin
                    features = log.get('features', {})
                    flat_log.update({f'feature_{k}': v for k, v in features.items()})
                flattened_logs.append(flat_log)
            
            if flattened_logs:
                writer = csv.DictWriter(output, fieldnames=flattened_logs[0].keys())
                writer.writeheader()
                writer.writerows(flattened_logs)
        
        from fastapi.responses import Response
        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=decision_logs_{datetime.utcnow().strftime('%Y%m%d')}.csv"}
        )
    
    return {"data": logs, "format": "json", "limit": "full" if has_full_export else "limited"}

@router.post("/retrain")
def trigger_retraining(
    current_user: User = Depends(require_permission(Permission.TRIGGER_RETRAINING)),
    db: Session = Depends(get_db)
):
    """Trigger model retraining (Admin only)"""
    # This would trigger the retraining pipeline
    # In a real system, this would be an async job
    return {
        "message": "Model retraining initiated",
        "status": "pending",
        "triggered_by": current_user.id,
        "triggered_at": datetime.utcnow()
    }

@router.get("/users", response_model=List[dict])
def list_users(
    current_user: User = Depends(require_permission(Permission.MANAGE_ROLES)),
    db: Session = Depends(get_db)
):
    """List all users (Admin only)"""
    users = db.query(User).all()
    return [
        {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "is_active": user.is_active,
            "created_at": user.created_at
        }
        for user in users
    ]

@router.put("/users/{user_id}/role", response_model=dict)
def update_user_role(
    user_id: int,
    new_role: str,
    current_user: User = Depends(require_permission(Permission.MANAGE_ROLES)),
    db: Session = Depends(get_db)
):
    """Update user role (Admin only)"""
    if new_role not in ["user", "auditor", "admin"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    old_role = user.role
    user.role = new_role
    db.commit()
    db.refresh(user)
    
    # Log to audit trail
    audit_data = {
        'action': 'role_change',
        'user_id': current_user.id,
        'user_role': current_user.role,
        'target_user_id': user_id,
        'old_role': old_role,
        'new_role': new_role
    }
    mongodb_client.insert_audit_trail(audit_data)
    
    return {
        "message": "User role updated",
        "user_id": user_id,
        "old_role": old_role,
        "new_role": new_role
    }

@router.get("/rules", response_model=dict)
def get_governance_rules(
    current_user: User = Depends(require_any_permission([
        Permission.VIEW_GOVERNANCE_RULES,
        Permission.CHANGE_GOVERNANCE_RULES
    ]))
):
    """Get governance rules (View for Auditor, Full for Admin)"""
    # This would return governance rules from config or database
    # For now, return a placeholder
    return {
        "fairness_threshold": 0.1,
        "retraining_trigger": "weekly",
        "audit_frequency": "daily",
        "data_retention_days": 365
    }

@router.put("/rules", response_model=dict)
def update_governance_rules(
    rules: dict,
    current_user: User = Depends(require_permission(Permission.CHANGE_GOVERNANCE_RULES)),
    db: Session = Depends(get_db)
):
    """Update governance rules (Admin only)"""
    # This would update governance rules in config or database
    # Log to audit trail
    audit_data = {
        'action': 'governance_rules_update',
        'user_id': current_user.id,
        'user_role': current_user.role,
        'rules': rules
    }
    mongodb_client.insert_audit_trail(audit_data)
    
    return {
        "message": "Governance rules updated",
        "rules": rules,
        "updated_by": current_user.id,
        "updated_at": datetime.utcnow()
    }

