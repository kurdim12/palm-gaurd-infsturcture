import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const getLatestReading = () => api.get('/api/sensors/latest')
export const getReadingHistory = (range = '1h') => api.get(`/api/sensors/history?range=${range}`)
export const controlPump = (state, user = 'operator') => api.post('/api/control/pump', { state, user })
export const doseNutrients = (amount_ml, user = 'operator') => api.post('/api/control/dose', { amount_ml, user })
export const getLatestAlerts = () => api.get('/api/alerts/latest')
export const getAlertHistory = () => api.get('/api/alerts/history')
export const startSimulator = () => api.post('/api/simulate/start')
export const stopSimulator = () => api.post('/api/simulate/stop')
export const getSimulatorStatus = () => api.get('/api/simulate/status')
export const getRoboCraftReport = () => api.get('/api/report/robocraft')
export const exportCSV = () => {
  window.open(`${API_BASE_URL}/api/report/export/csv`, '_blank')
}

export default api
