import { useAuth } from '../context/AuthContext'

// Permission mappings based on role
const ROLE_PERMISSIONS = {
  user: [
    'apply_for_loan',
    'view_own_shap',
    'voice_assistant_full',
    'manage_consent',
    'view_profile_explanation',
    'view_own_logs',
  ],
  auditor: [
    'view_all_explanations',
    'voice_assistant_limited',
    'view_all_logs',
    'export_logs_limited',
    'view_fairness_metrics',
    'override_decision_recommend',
    'view_governance_rules',
  ],
  admin: [
    'view_all_explanations',
    'voice_assistant_full',
    'configure_consent_defaults',
    'view_all_logs',
    'export_logs_full',
    'view_fairness_metrics',
    'trigger_retraining',
    'override_decision_approve',
    'manage_roles',
    'view_governance_rules',
    'change_governance_rules',
  ],
}

export const usePermissions = () => {
  const { user } = useAuth()

  const hasPermission = (permission) => {
    if (!user) return false
    const userPermissions = ROLE_PERMISSIONS[user.role] || []
    return userPermissions.includes(permission)
  }

  const hasAnyPermission = (permissions) => {
    return permissions.some(permission => hasPermission(permission))
  }

  const hasAllPermissions = (permissions) => {
    return permissions.every(permission => hasPermission(permission))
  }

  const isRole = (role) => {
    return user?.role === role
  }

  const isAdmin = () => {
    return user?.role === 'admin'
  }

  const isAuditor = () => {
    return user?.role === 'auditor'
  }

  const isUser = () => {
    return user?.role === 'user'
  }

  return {
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    isRole,
    isAdmin,
    isAuditor,
    isUser,
    userRole: user?.role,
  }
}

