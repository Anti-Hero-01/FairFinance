import api from './api'

export const consentService = {
  async getDashboard() {
    const response = await api.get('/consent/dashboard')
    return response.data
  },

  async updateConsent(dataCategory, consentGiven) {
    const response = await api.post('/consent/update', {
      data_category: dataCategory,
      consent_given: consentGiven
    })
    return response.data
  },

  async getAlerts() {
    const response = await api.get('/consent/alerts')
    return response.data
  },
}

