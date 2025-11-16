import api from './api'

export const authService = {
  async login(email, password) {
    const response = await api.post('/auth/login', { email, password })
    return response.data
  },

  async register(userData) {
    const response = await api.post('/auth/register', userData)
    return response.data
  },

  async getCurrentUser(token) {
    const response = await api.get('/auth/me', {
      headers: { Authorization: `Bearer ${token}` }
    })
    return response.data
  },
}

