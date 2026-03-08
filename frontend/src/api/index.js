import axios from 'axios'

const API_BASE_URL = 'http://localhost:5000/api'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
apiClient.interceptors.request.use(
  config => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

// Response interceptor for token refresh
apiClient.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      try {
        const refreshToken = localStorage.getItem('refresh_token')
        const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {}, {
          headers: { Authorization: `Bearer ${refreshToken}` }
        })
        
        if (response.data.access_token) {
          localStorage.setItem('access_token', response.data.access_token)
          originalRequest.headers.Authorization = `Bearer ${response.data.access_token}`
          return apiClient(originalRequest)
        }
      } catch (refreshError) {
        localStorage.clear()
        window.location.href = '/login'
      }
    }
    
    return Promise.reject(error)
  }
)

const api = {
  // Auth
  login: (credentials) => apiClient.post('/auth/login', credentials),
  register: (userData) => apiClient.post('/auth/register', userData),
  logout: () => apiClient.post('/auth/logout'),
  getProfile: () => apiClient.get('/auth/profile'),
  
  // Admin
  getAdminDashboard: () => apiClient.get('/admin/dashboard'),
  getDoctors: () => apiClient.get('/admin/doctors'),
  addDoctor: (doctorData) => apiClient.post('/admin/doctors', doctorData),
  updateDoctor: (id, data) => apiClient.put(`/admin/doctors/${id}`, data),
  deleteDoctor: (id) => apiClient.delete(`/admin/doctors/${id}`),
  getPatients: () => apiClient.get('/admin/patients'),
  deletePatient: (id) => apiClient.delete(`/admin/patients/${id}`),
  getAllAppointments: () => apiClient.get('/admin/appointments'),
  search: (query, type) => {
    const params = new URLSearchParams()
    if (query) params.append('q', query)
    if (type) params.append('type', type)
    return apiClient.get(`/admin/search?${params.toString()}`)
  },
  getDepartments: () => apiClient.get('/admin/departments'),
  
  // Doctor
  getDoctorDashboard: () => apiClient.get('/doctor/dashboard'),
  getDoctorAppointments: (status, from, to) => {
    const params = new URLSearchParams()
    if (status) params.append('status', status)
    if (from) params.append('from', from)
    if (to) params.append('to', to)
    return apiClient.get(`/doctor/appointments?${params.toString()}`)
  },
  updateAppointmentStatus: (id, status) => 
    apiClient.put(`/doctor/appointments/${id}/status`, { status }),
  saveTreatment: (appointmentId, treatmentData) => 
    apiClient.post(`/doctor/appointments/${appointmentId}/treatment`, treatmentData),
  getPatientHistory: (patientId) => apiClient.get(`/doctor/patients/${patientId}/history`),
  updateAvailability: (availability) => apiClient.put('/doctor/availability', { availability }),
  getAvailability: () => apiClient.get('/doctor/availability'),
  
  // Patient
  getPatientDashboard: () => apiClient.get('/patient/dashboard'),
  updatePatientProfile: (profileData) => apiClient.put('/patient/profile', profileData),
  searchDoctors: (specialization, name) => {
    const params = new URLSearchParams()
    if (specialization) params.append('specialization', specialization)
    if (name) params.append('name', name)
    return apiClient.get(`/patient/doctors?${params.toString()}`)
  },
  getDoctorAvailability: (doctorId) => apiClient.get(`/patient/doctors/${doctorId}/availability`),
  bookAppointment: (appointmentData) => apiClient.post('/patient/appointments', appointmentData),
  rescheduleAppointment: (id, date, time) => 
    apiClient.put(`/patient/appointments/${id}`, { date, time }),
  cancelAppointment: (id) => apiClient.delete(`/patient/appointments/${id}`),
  getMyAppointments: (status) => {
    const params = new URLSearchParams()
    if (status) params.append('status', status)
    return apiClient.get(`/patient/appointments${params.toString() ? '?' + params.toString() : ''}`)
  },
  getTreatmentHistory: () => apiClient.get('/patient/treatments')
}

export default api