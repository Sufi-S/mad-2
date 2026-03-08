<template>
  <div>
    <!-- Page Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>
        <i class="fas fa-tachometer-alt me-2"></i>
        Patient Dashboard
      </h2>
      <button class="btn btn-primary" @click="showProfileModal = true">
        <i class="fas fa-user-edit me-2"></i>
        Edit Profile
      </button>
    </div>

    <!-- Departments/Specializations -->
    <div class="card mb-4">
      <div class="card-header">
        <i class="fas fa-stethoscope me-2"></i>
        Available Specializations
      </div>
      <div class="card-body">
        <div class="row">
          <div class="col-md-3 mb-3" v-for="dept in departments" :key="dept.id">
            <div class="card bg-dark h-100" @click="searchBySpecialization(dept.name)" style="cursor: pointer;">
              <div class="card-body text-center">
                <i class="fas fa-heartbeat fa-3x mb-3 text-white-50"></i>
                <h6 class="card-title">{{ dept.name }}</h6>
                <p class="card-text small text-muted">{{ dept.description }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Upcoming Appointments -->
    <div class="card mb-4">
      <div class="card-header">
        <i class="fas fa-calendar-alt me-2"></i>
        Upcoming Appointments
      </div>
      <div class="card-body">
        <div v-if="upcomingAppointments.length === 0" class="text-center text-muted py-4">
          <i class="fas fa-calendar-plus fa-3x mb-3"></i>
          <p>No upcoming appointments</p>
          <router-link to="/patient/book-appointment" class="btn btn-primary">
            <i class="fas fa-plus me-2"></i>
            Book Appointment
          </router-link>
        </div>
        
        <div v-else class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>Doctor</th>
                <th>Specialization</th>
                <th>Date</th>
                <th>Time</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="apt in upcomingAppointments" :key="apt.id">
                <td>{{ apt.doctor_name }}</td>
                <td>{{ apt.doctor?.specialization || 'N/A' }}</td>
                <td>{{ formatDate(apt.appointment_date) }}</td>
                <td>{{ apt.appointment_time }}</td>
                <td>
                  <span class="badge bg-warning">{{ apt.status }}</span>
                </td>
                <td>
                  <button class="btn btn-sm btn-danger" @click="cancelAppointment(apt)">
                    <i class="fas fa-times me-1"></i>
                    Cancel
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Past Appointments -->
    <div class="card">
      <div class="card-header">
        <i class="fas fa-history me-2"></i>
        Past Appointments
      </div>
      <div class="card-body">
        <div v-if="pastAppointments.length === 0" class="text-center text-muted py-4">
          <i class="fas fa-calendar-times fa-3x mb-3"></i>
          <p>No past appointments</p>
        </div>
        
        <div v-else class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>Date</th>
                <th>Doctor</th>
                <th>Specialization</th>
                <th>Diagnosis</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="apt in pastAppointments" :key="apt.id">
                <td>{{ formatDate(apt.appointment_date) }}</td>
                <td>{{ apt.doctor_name }}</td>
                <td>{{ apt.doctor?.specialization || 'N/A' }}</td>
                <td>{{ apt.treatment?.diagnosis || 'N/A' }}</td>
                <td>
                  <button class="btn btn-sm btn-info" @click="viewTreatment(apt)">
                    <i class="fas fa-eye me-1"></i>
                    View Details
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Edit Profile Modal -->
    <div class="modal fade" id="profileModal" tabindex="-1" ref="profileModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              <i class="fas fa-user-edit me-2"></i>
              Edit Profile
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="updateProfile">
              <div class="form-group mb-3">
                <label class="form-label">Full Name</label>
                <input type="text" class="form-control" v-model="profile.name" required>
              </div>

              <div class="form-group mb-3">
                <label class="form-label">Phone Number</label>
                <input type="tel" class="form-control" v-model="profile.phone" required>
              </div>

              <div class="form-group mb-3">
                <label class="form-label">Date of Birth</label>
                <input type="date" class="form-control" v-model="profile.date_of_birth">
              </div>

              <div class="form-group mb-3">
                <label class="form-label">Gender</label>
                <select class="form-select" v-model="profile.gender">
                  <option value="">Select Gender</option>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="other">Other</option>
                </select>
              </div>

              <div class="form-group mb-3">
                <label class="form-label">Blood Group</label>
                <select class="form-select" v-model="profile.blood_group">
                  <option value="">Select Blood Group</option>
                  <option value="A+">A+</option>
                  <option value="A-">A-</option>
                  <option value="B+">B+</option>
                  <option value="B-">B-</option>
                  <option value="O+">O+</option>
                  <option value="O-">O-</option>
                  <option value="AB+">AB+</option>
                  <option value="AB-">AB-</option>
                </select>
              </div>

              <div class="form-group mb-3">
                <label class="form-label">Emergency Contact</label>
                <input type="tel" class="form-control" v-model="profile.emergency_contact">
              </div>

              <div class="form-group mb-3">
                <label class="form-label">Address</label>
                <textarea class="form-control" rows="2" v-model="profile.address"></textarea>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-primary" @click="updateProfile" :disabled="saving">
              <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
              <i v-else class="fas fa-save me-2"></i>
              Save Changes
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PatientDashboard',
  data() {
    return {
      departments: [],
      upcomingAppointments: [],
      pastAppointments: [],
      profile: {},
      saving: false,
      showProfileModal: false
    }
  },
  mounted() {
    this.fetchDashboard()
    this.fetchProfile()
    this.profileModal = new bootstrap.Modal(this.$refs.profileModal)
  },
  watch: {
    showProfileModal(val) {
      if (val) {
        this.profileModal.show()
      } else {
        this.profileModal.hide()
      }
    }
  },
  methods: {
    async fetchDashboard() {
      try {
        const response = await this.$api.getPatientDashboard()
        const data = response.data
        
        this.departments = data.departments || []
        this.upcomingAppointments = data.upcoming_appointments || []
        this.pastAppointments = data.past_appointments || []
        
      } catch (error) {
        console.error('Error fetching dashboard:', error)
      }
    },
    
    fetchProfile() {
      const savedProfile = localStorage.getItem('profile')
      if (savedProfile) {
        this.profile = JSON.parse(savedProfile)
      }
    },
    
    async updateProfile() {
      this.saving = true
      try {
        const response = await this.$api.updatePatientProfile(this.profile)
        localStorage.setItem('profile', JSON.stringify(response.data.profile))
        this.showProfileModal = false
        alert('Profile updated successfully!')
      } catch (error) {
        alert(error.response?.data?.error || 'Error updating profile')
      } finally {
        this.saving = false
      }
    },
    
    async cancelAppointment(appointment) {
      if (confirm(`Cancel appointment with Dr. ${appointment.doctor_name}?`)) {
        try {
          await this.$api.cancelAppointment(appointment.id)
          await this.fetchDashboard()
        } catch (error) {
          alert('Error cancelling appointment')
        }
      }
    },
    
    viewTreatment(appointment) {
      this.$router.push(`/treatment-history?appointment=${appointment.id}`)
    },
    
    searchBySpecialization(specialization) {
      this.$router.push(`/patient/book-appointment?specialization=${specialization}`)
    },
    
    formatDate(date) {
      return new Date(date).toLocaleDateString()
    }
  }
}
</script>