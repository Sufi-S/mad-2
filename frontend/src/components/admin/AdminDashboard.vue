<template>
  <div>
    <!-- Page Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>
        <i class="fas fa-tachometer-alt me-2"></i>
        Admin Dashboard
      </h2>
      <div>
        <button class="btn btn-primary me-2" @click="refreshData">
          <i class="fas fa-sync-alt me-2"></i>
          Refresh
        </button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="row mb-4">
      <div class="col-md-3 mb-3">
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-user-md"></i>
          </div>
          <div class="stat-value">{{ stats.total_doctors || 0 }}</div>
          <div class="stat-label">Total Doctors</div>
        </div>
      </div>
      <div class="col-md-3 mb-3">
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-users"></i>
          </div>
          <div class="stat-value">{{ stats.total_patients || 0 }}</div>
          <div class="stat-label">Total Patients</div>
        </div>
      </div>
      <div class="col-md-3 mb-3">
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-calendar-check"></i>
          </div>
          <div class="stat-value">{{ stats.total_appointments || 0 }}</div>
          <div class="stat-label">Total Appointments</div>
        </div>
      </div>
      <div class="col-md-3 mb-3">
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-chart-line"></i>
          </div>
          <div class="stat-value">{{ stats.appointment_stats?.completed || 0 }}</div>
          <div class="stat-label">Completed</div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="card">
          <div class="card-header">
            <i class="fas fa-bolt me-2"></i>
            Quick Actions
          </div>
          <div class="card-body">
            <div class="row">
              <div class="col-md-3 mb-2">
                <router-link to="/admin/doctors" class="btn btn-secondary w-100">
                  <i class="fas fa-user-md me-2"></i>
                  Manage Doctors
                </router-link>
              </div>
              <div class="col-md-3 mb-2">
                <button class="btn btn-secondary w-100" @click="showSearch = !showSearch">
                  <i class="fas fa-search me-2"></i>
                  Search
                </button>
              </div>
              <div class="col-md-3 mb-2">
                <button class="btn btn-secondary w-100" @click="exportReport">
                  <i class="fas fa-file-export me-2"></i>
                  Export Report
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Search Section -->
    <div v-if="showSearch" class="card mb-4">
      <div class="card-header">
        <i class="fas fa-search me-2"></i>
        Search Patients / Doctors
      </div>
      <div class="card-body">
        <div class="row">
          <div class="col-md-6">
            <div class="input-group">
              <input 
                type="text" 
                class="form-control" 
                placeholder="Search by name, specialization, phone..." 
                v-model="searchQuery"
                @keyup.enter="performSearch"
              >
              <button class="btn btn-primary" type="button" @click="performSearch">
                <i class="fas fa-search"></i>
              </button>
            </div>
          </div>
          <div class="col-md-3">
            <select class="form-select" v-model="searchType">
              <option value="all">All</option>
              <option value="doctors">Doctors Only</option>
              <option value="patients">Patients Only</option>
            </select>
          </div>
        </div>
        
        <!-- Search Results -->
        <div v-if="searchResults" class="mt-4">
          <div v-if="searchResults.doctors?.length" class="mb-4">
            <h6 class="text-white-50 mb-3">
              <i class="fas fa-user-md me-2"></i>
              Doctors ({{ searchResults.doctors.length }})
            </h6>
            <div class="table-responsive">
              <table class="table table-hover">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Specialization</th>
                    <th>Experience</th>
                    <th>Fee</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="doctor in searchResults.doctors" :key="doctor.id">
                    <td>{{ doctor.name }}</td>
                    <td>{{ doctor.specialization }}</td>
                    <td>{{ doctor.experience_years || 0 }} years</td>
                    <td>${{ doctor.consultation_fee || 0 }}</td>
                    <td>
                      <router-link :to="'/admin/doctors?edit=' + doctor.id" class="btn btn-sm btn-primary me-1">
                        <i class="fas fa-edit"></i>
                      </router-link>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          
          <div v-if="searchResults.patients?.length">
            <h6 class="text-white-50 mb-3">
              <i class="fas fa-users me-2"></i>
              Patients ({{ searchResults.patients.length }})
            </h6>
            <div class="table-responsive">
              <table class="table table-hover">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Phone</th>
                    <th>Blood Group</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="patient in searchResults.patients" :key="patient.id">
                    <td>{{ patient.name }}</td>
                    <td>{{ patient.phone }}</td>
                    <td>{{ patient.blood_group || 'N/A' }}</td>
                    <td>
                      <button class="btn btn-sm btn-danger" @click="confirmDeletePatient(patient)">
                        <i class="fas fa-trash"></i>
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div v-if="!searchResults.doctors?.length && !searchResults.patients?.length" class="text-center text-muted py-4">
            <i class="fas fa-search fa-3x mb-3"></i>
            <p>No results found</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Appointments -->
    <div class="card">
      <div class="card-header">
        <i class="fas fa-calendar-alt me-2"></i>
        Recent Appointments
      </div>
      <div class="card-body">
        <div v-if="loading" class="text-center py-4">
          <div class="spinner-border" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>
        
        <div v-else-if="appointments.length === 0" class="text-center text-muted py-4">
          <i class="fas fa-calendar-times fa-3x mb-3"></i>
          <p>No appointments found</p>
        </div>
        
        <div v-else class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>ID</th>
                <th>Patient</th>
                <th>Doctor</th>
                <th>Date</th>
                <th>Time</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="apt in appointments" :key="apt.id">
                <td>#{{ apt.id }}</td>
                <td>{{ apt.patient_name }}</td>
                <td>{{ apt.doctor_name }}</td>
                <td>{{ formatDate(apt.appointment_date) }}</td>
                <td>{{ apt.appointment_time }}</td>
                <td>
                  <span class="badge" :class="{
                    'bg-success': apt.status === 'completed',
                    'bg-warning': apt.status === 'booked',
                    'bg-danger': apt.status === 'cancelled'
                  }">
                    {{ apt.status }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div class="modal fade" id="deleteModal" tabindex="-1" ref="deleteModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              <i class="fas fa-exclamation-triangle text-danger me-2"></i>
              Confirm Delete
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            Are you sure you want to delete {{ deleteTarget?.name }}?
            <p class="text-muted mt-2">
              <small>This will deactivate the user account. This action can be undone by reactivating.</small>
            </p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-danger" @click="deleteConfirmed">
              <i class="fas fa-trash me-2"></i>
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AdminDashboard',
  data() {
    return {
      stats: {},
      appointments: [],
      searchQuery: '',
      searchType: 'all',
      searchResults: null,
      showSearch: false,
      loading: false,
      deleteTarget: null
    }
  },
  mounted() {
    this.fetchData()
    this.deleteModal = new bootstrap.Modal(this.$refs.deleteModal)
  },
  methods: {
    async fetchData() {
      this.loading = true
      try {
        const [dashboard, appointments] = await Promise.all([
          this.$api.getAdminDashboard(),
          this.$api.getAllAppointments()
        ])
        
        this.stats = dashboard.data
        this.appointments = appointments.data.slice(0, 10) // Last 10 appointments
        
      } catch (error) {
        console.error('Error fetching data:', error)
      } finally {
        this.loading = false
      }
    },
    
    async refreshData() {
      await this.fetchData()
    },
    
    async performSearch() {
      if (!this.searchQuery.trim()) {
        this.searchResults = null
        return
      }
      
      try {
        const response = await this.$api.search(this.searchQuery, this.searchType)
        this.searchResults = response.data
      } catch (error) {
        console.error('Search error:', error)
      }
    },
    
    confirmDeletePatient(patient) {
      this.deleteTarget = { type: 'patient', id: patient.id, name: patient.name }
      this.deleteModal.show()
    },
    
    async deleteConfirmed() {
      try {
        if (this.deleteTarget.type === 'patient') {
          await this.$api.deletePatient(this.deleteTarget.id)
        }
        
        this.deleteModal.hide()
        this.searchResults = null
        this.searchQuery = ''
        await this.fetchData()
        
      } catch (error) {
        alert('Error deleting user')
      }
    },
    
    formatDate(date) {
      return new Date(date).toLocaleDateString()
    },
    
    exportReport() {
      // TODO: Implement report export
      alert('Report export feature coming soon!')
    }
  }
}
</script>