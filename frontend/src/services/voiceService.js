import api from './api'

export const voiceService = {
  async processQuery(audioData, language, applicationId, userId) {
    const response = await api.post('/voice/ask', {
      audio_data: audioData,
      language: language || 'en',
      application_id: applicationId || null,
      user_id: userId || null
    })
    return response.data
  },
}

