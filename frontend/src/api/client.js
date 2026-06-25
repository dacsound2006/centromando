import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/mando',
  headers: { 'Content-Type': 'application/json' },
})

export default {
  // Tareas
  getTasks: () => api.get('/tasks/'),
  addTask: (data) => api.post('/tasks/', data),
  toggleTask: (id) => api.post(`/tasks/${id}/toggle/`),
  moveTask: (id, list) => api.post(`/tasks/${id}/move/`, { list }),
  deleteTask: (id) => api.delete(`/tasks/${id}/`),

  // OKRs
  getObjectives: () => api.get('/objectives/'),
  addObjective: (data) => api.post('/objectives/', data),
  updateObjective: (id, data) => api.patch(`/objectives/${id}/`, data),
  deleteObjective: (id) => api.delete(`/objectives/${id}/`),
  setKrProgress: (id, progress) => api.post(`/keyresults/${id}/progress/`, { progress }),
  addKeyResult: (data) => api.post('/keyresults/', data),
  updateKeyResult: (id, data) => api.patch(`/keyresults/${id}/`, data),
  deleteKeyResult: (id) => api.delete(`/keyresults/${id}/`),

  // Tendencias
  getTrends: () => api.get('/trends/'),
  addTrend: (data) => api.post('/trends/', data),
  toggleTrend: (id) => api.post(`/trends/${id}/toggle/`),
  deleteTrend: (id) => api.delete(`/trends/${id}/`),

  // Ritmos / hábitos
  getRhythms: () => api.get('/rhythms/'),
  toggleRhythm: (rhythm, day) => api.post('/rhythms/toggle/', { rhythm, day }),

  // Revisión semanal
  getReview: () => api.get('/review/'),
  toggleReview: (id) => api.post(`/review/${id}/toggle/`),
  resetReview: () => api.post('/review/reset/'),
}
