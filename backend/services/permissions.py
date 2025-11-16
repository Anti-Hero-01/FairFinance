"""
Permission management service for role-based access control
"""
from enum import Enum
from typing import List
from fastapi import Depends, HTTPException, status
from backend.models.database import User
from backend.services.auth import get_current_active_user

class Permission(str, Enum):
    # User permissions
    APPLY_FOR_LOAN = "apply_for_loan"
    VIEW_OWN_SHAP = "view_own_shap"
    VIEW_PROFILE_EXPLANATION = "view_profile_explanation"
    MANAGE_CONSENT = "manage_consent"
    VIEW_OWN_LOGS = "view_own_logs"
    VOICE_ASSISTANT_FULL = "voice_assistant_full"
    
    # Auditor permissions
    VIEW_ALL_EXPLANATIONS = "view_all_explanations"
    VIEW_ALL_LOGS = "view_all_logs"
    VIEW_FAIRNESS_METRICS = "view_fairness_metrics"
    EXPORT_LOGS_LIMITED = "export_logs_limited"
    OVERRIDE_DECISION_RECOMMEND = "override_decision_recommend"
    VIEW_GOVERNANCE_RULES = "view_governance_rules"
    VOICE_ASSISTANT_LIMITED = "voice_assistant_limited"
    
    # Admin permissions
    CONFIGURE_CONSENT_DEFAULTS = "configure_consent_defaults"
    EXPORT_LOGS_FULL = "export_logs_full"
    TRIGGER_RETRAINING = "trigger_retraining"
    OVERRIDE_DECISION_APPROVE = "override_decision_approve"
    MANAGE_ROLES = "manage_roles"
    CHANGE_GOVERNANCE_RULES = "change_governance_rules"

# Role to permissions mapping
ROLE_PERMISSIONS = {
    "user": [
        Permission.APPLY_FOR_LOAN,
        Permission.VIEW_OWN_SHAP,
        Permission.VIEW_PROFILE_EXPLANATION,
        Permission.MANAGE_CONSENT,
        Permission.VIEW_OWN_LOGS,
        Permission.VOICE_ASSISTANT_FULL,
    ],
    "auditor": [
        Permission.VIEW_ALL_EXPLANATIONS,
        Permission.VIEW_ALL_LOGS,
        Permission.VIEW_FAIRNESS_METRICS,
        Permission.EXPORT_LOGS_LIMITED,
        Permission.OVERRIDE_DECISION_RECOMMEND,
        Permission.VIEW_GOVERNANCE_RULES,
        Permission.VOICE_ASSISTANT_LIMITED,
    ],
    "admin": [
        Permission.VIEW_ALL_EXPLANATIONS,
        Permission.VIEW_ALL_LOGS,
        Permission.VIEW_FAIRNESS_METRICS,
        Permission.EXPORT_LOGS_FULL,
        Permission.TRIGGER_RETRAINING,
        Permission.OVERRIDE_DECISION_APPROVE,
        Permission.MANAGE_ROLES,
        Permission.VIEW_GOVERNANCE_RULES,
        Permission.CHANGE_GOVERNANCE_RULES,
        Permission.CONFIGURE_CONSENT_DEFAULTS,
        Permission.VOICE_ASSISTANT_FULL,
    ],
}

def has_permission(user: User, permission: Permission) -> bool:
    """Check if user has a specific permission"""
    if not user or not user.role:
        return False
    user_permissions = ROLE_PERMISSIONS.get(user.role, [])
    return permission in user_permissions

def require_permission(permission: Permission):
    """Dependency to require a specific permission"""
    def permission_checker(current_user: User = Depends(get_current_active_user)):
        if not has_permission(current_user, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required: {permission.value}"
            )
        return current_user
    return permission_checker

def require_any_permission(permissions: List[Permission]):
    """Dependency to require any of the specified permissions"""
    def permission_checker(current_user: User = Depends(get_current_active_user)):
        if not any(has_permission(current_user, perm) for perm in permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required one of: {[p.value for p in permissions]}"
            )
        return current_user
    return permission_checker

def require_own_resource_or_permission(permission: Permission):
    """Dependency to allow access if user owns the resource OR has the permission"""
    def permission_checker(current_user: User = Depends(get_current_active_user)):
        # This will be checked at the route level for resource ownership
        # Here we just ensure the user is authenticated
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        return current_user
    return permission_checker

