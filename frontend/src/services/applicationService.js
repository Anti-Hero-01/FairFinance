import api from './api'

export const applicationService = {
  async predict(applicationData) {
    const response = await api.post('/predict', {
      application_data: applicationData
    })
    return response.data
  },

  async getApplications() {
    const response = await api.get('/predict/applications')
    return response.data
  },

  async getApplication(applicationId) {
    const response = await api.get(`/predict/applications/${applicationId}`)
    return response.data
  },

  async getExplanation(applicationId) {
    const response = await api.get(`/explain/${applicationId}`)
    return response.data
  },
}

