import api from './api'

export const governanceService = {
  async getDecisionLogs() {
    const response = await api.get(`/governance/decision-logs`)
    return response.data
  },

  async getDecisionLog(userId) {
    const response = await api.get(`/governance/decision-log/${userId}`)
    return response.data
  },

  async getFairnessReport() {
    const response = await api.get('/governance/fairness-report')
    return response.data
  },

  async adminOverride(applicationId, newDecision, reason) {
    const response = await api.post('/governance/admin/override', {
      application_id: applicationId,
      new_decision: newDecision,
      reason: reason
    })
    return response.data
  },

  async getAuditTrail(limit = 100) {
    const response = await api.get(`/governance/audit-trail?limit=${limit}`)
    return response.data
  },

  async exportLogs(userId = null, format = 'json') {
    const params = new URLSearchParams({ format })
    if (userId) params.append('user_id', userId)
    const response = await api.get(`/governance/export-logs?${params}`, {
      responseType: format === 'csv' ? 'blob' : 'json'
    })
    return response
  },

  async triggerRetraining() {
    const response = await api.post('/governance/retrain')
    return response.data
  },

  async listUsers() {
    const response = await api.get('/governance/users')
    return response.data
  },

  async updateUserRole(userId, newRole) {
    const response = await api.put(`/governance/users/${userId}/role`, null, {
      params: { new_role: newRole }
    })
    return response.data
  },

  async getGovernanceRules() {
    const response = await api.get('/governance/rules')
    return response.data
  },

  async updateGovernanceRules(rules) {
    const response = await api.put('/governance/rules', rules)
    return response.data
  },
}

