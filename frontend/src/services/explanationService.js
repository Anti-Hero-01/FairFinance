import api from './api'

export const explanationService = {
  async explainProfile(userId) {
    const response = await api.post('/explain/profile', {
      user_id: userId
    })
    return response.data
  },
}

