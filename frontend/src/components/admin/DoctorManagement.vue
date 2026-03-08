<template>
  <div>
    <!-- Page Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>
        <i class="fas fa-user-md me-2"></i>
        Doctor Management
      </h2>
      <button class="btn btn-primary" @click="openAddModal">
        <i class="fas fa-plus me-2"></i>
        Add New Doctor
      </button>
    </div>

    <!-- Doctors List -->
    <div class="card">
      <div class="card-header">
        <div class="row align-items-center">
          <div class="col-md-6">
            <i class="fas fa-list me-2"></i>
            All Doctors
          </div>
          <div class="col-md-6">
            <div class="input-group">
              <input 
                type="text" 
                class="form-control" 
                placeholder="Search doctors..." 
                v-model="searchQuery"
                @keyup="filterDoctors"
              >
              <span class="input-group-text">
                <i class="fas fa-search"></i>
              </span>
            </div>
          </div>
        </div>
      </div>
      <div class="card-body">
        <div v-if="loading" class="text-center py-4">
          <div class="spinner-border" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>
        
        <div v-else-if="filteredDoctors.length === 0" class="text-center text-muted py-4">
          <i class="fas fa-user-md fa-3x mb-3"></i>
          <p>No doctors found</p>
        </div>
        
        <div v-else class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Specialization</th>
                <th>Qualification</th>
                <th>Experience</th>
                <th>Fee</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="doctor in filteredDoctors" :key="doctor.id">
                <td>#{{ doctor.id }}</td>
                <td>
                  <strong>{{ doctor.name }}</strong>
                  <br>
                  <small class="text-muted">{{ doctor.user?.email }}</small>
                </td>
                <td>{{ doctor.specialization }}</td>
                <td>{{ doctor.qualification || 'N/A' }}</td>
                <td>{{ doctor.experience_years || 0 }} years</td>
                <td>${{ doctor.consultation_fee || 0 }}</td>
                <td>
                  <span class="badge" :class="doctor.user?.is_active ? 'bg-success' : 'bg-danger'">
                    {{ doctor.user?.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </td>
                <td>
                  <button class="btn btn-sm btn-primary me-1" @click="editDoctor(doctor)">
                    <i class="fas fa-edit"></i>
                  </button>
                  <button class="btn btn-sm" :class="doctor.user?.is_active ? 'btn-danger' : 'btn-success'" 
                          @click="toggleDoctorStatus(doctor)">
                    <i class="fas" :class="doctor.user?.is_active ? 'fa-ban' : 'fa-check'"></i>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Add/Edit Doctor Modal -->
    <div class="modal fade" id="doctorModal" tabindex="-1" ref="doctorModal">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              <i class="fas" :class="editingDoctor ? 'fa-edit' : 'fa-user-md'"></i>
              {{ editingDoctor ? 'Edit Doctor' : 'Add New Doctor' }}
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="saveDoctor">
              <!-- Account Information -->
              <h6 class="text-white-50 mb-3">Account Information</h6>
              
              <div class="row mb-3">
                <div class="col-md-6">
                  <label class="form-label">Username *</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    v-model="doctorForm.username" 
                    required
                    :disabled="editingDoctor"
                  >
                </div>
                <div class="col-md-6">
                  <label class="form-label">Email *</label>
                  <input 
                    type="email" 
                    class="form-control" 
                    v-model="doctorForm.email" 
                    required
                    :disabled="editingDoctor"
                  >
                </div>
              </div>

              <div v-if="!editingDoctor" class="row mb-4">
                <div class="col-md-6">
                  <label class="form-label">Password</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    v-model="doctorForm.password" 
                    readonly
                    value="doctor123"
                  >
                  <small class="text-muted">Default password: doctor123</small>
                </div>
              </div>

              <!-- Professional Information -->
              <h6 class="text-white-50 mb-3">Professional Information</h6>

              <div class="row mb-3">
                <div class="col-md-6">
                  <label class="form-label">Full Name *</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    v-model="doctorForm.name" 
                    required
                  >
                </div>
                <div class="col-md-6">
                  <label class="form-label">Specialization *</label>
                  <select class="form-select" v-model="doctorForm.specialization" required>
                    <option value="">Select Specialization</option>
                    <option v-for="dept in departments" :key="dept.id" :value="dept.name">
                      {{ dept.name }}
                    </option>
                  </select>
                </div>
              </div>

              <div class="row mb-3">
                <div class="col-md-6">
                  <label class="form-label">Qualification</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    v-model="doctorForm.qualification"
                    placeholder="e.g., MBBS, MD"
                  >
                </div>
                <div class="col-md-6">
                  <label class="form-label">Experience (years)</label>
                  <input 
                    type="number" 
                    class="form-control" 
                    v-model="doctorForm.experience_years"
                    min="0"
                  >
                </div>
              </div>

              <div class="row mb-4">
                <div class="col-md-6">
                  <label class="form-label">Consultation Fee ($)</label>
                  <input 
                    type="number" 
                    step="0.01" 
                    class="form-control" 
                    v-model="doctorForm.consultation_fee"
                    min="0"
                  >
                </div>
              </div>

              <!-- Weekly Availability -->
              <h6 class="text-white-50 mb-3">Weekly Availability</h6>
              <div class="row mb-3">
                <div class="col-12">
                  <div class="table-responsive">
                    <table class="table table-sm">
                      <thead>
                        <tr>
                          <th>Day</th>
                          <th>Available</th>
                          <th>Time Slots</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="(day, index) in weekDays" :key="index">
                          <td>{{ day }}</td>
                          <td>
                            <input 
                              type="checkbox" 
                              class="form-check-input" 
                              v-model="availability[day].enabled"
                              @change="updateAvailability(day)"
                            >
                          </td>
                          <td>
                            <div v-if="availability[day].enabled" class="d-flex flex-wrap gap-2">
                              <span 
                                v-for="(slot, slotIdx) in timeSlots" 
                                :key="slotIdx"
                                class="badge"
                                :class="availability[day].slots.includes(slot) ? 'bg-success' : 'bg-secondary'"
                                @click="toggleTimeSlot(day, slot)"
                              >
                                {{ slot }}
                              </span>
                            </div>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-primary" @click="saveDoctor">
              {{ editingDoctor ? 'Update Doctor' : 'Add Doctor' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DoctorManagement',
  data() {
    return {
      doctors: [],
      departments: [],
      filteredDoctors: [],
      searchQuery: '',
      loading: false,
      editingDoctor: null,
      doctorForm: {
        username: '',
        email: '',
        password: 'doctor123',
        name: '',
        specialization: '',
        qualification: '',
        experience_years: 0,
        consultation_fee: 0
      },
      availability: {},
      weekDays: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
      timeSlots: ['09:00', '10:00', '11:00', '14:00', '15:00', '16:00']
    }
  },
  mounted() {
    this.fetchDoctors()
    this.fetchDepartments()
    this.initAvailability()
    this.doctorModal = new bootstrap.Modal(this.$refs.doctorModal)
  },
  methods: {
    async fetchDoctors() {
      this.loading = true
      try {
        const response = await this.$api.getDoctors()
        this.doctors = response.data
        this.filteredDoctors = response.data
      } catch (error) {
        console.error('Error fetching doctors:', error)
      } finally {
        this.loading = false
      }
    },
    
    async fetchDepartments() {
      try {
        const response = await this.$api.getDepartments()
        this.departments = response.data
      } catch (error) {
        console.error('Error fetching departments:', error)
      }
    },
    
    initAvailability() {
      this.weekDays.forEach(day => {
        this.availability[day] = {
          enabled: false,
          slots: []
        }
      })
    },
    
    filterDoctors() {
      if (!this.searchQuery) {
        this.filteredDoctors = this.doctors
        return
      }
      
      const query = this.searchQuery.toLowerCase()
      this.filteredDoctors = this.doctors.filter(doctor => 
        doctor.name.toLowerCase().includes(query) ||
        doctor.specialization.toLowerCase().includes(query) ||
        doctor.qualification?.toLowerCase().includes(query)
      )
    },
    
    openAddModal() {
      this.editingDoctor = null
      this.doctorForm = {
        username: '',
        email: '',
        password: 'doctor123',
        name: '',
        specialization: '',
        qualification: '',
        experience_years: 0,
        consultation_fee: 0
      }
      this.initAvailability()
      this.doctorModal.show()
    },
    
    editDoctor(doctor) {
      this.editingDoctor = doctor
      this.doctorForm = {
        username: doctor.user?.username || '',
        email: doctor.user?.email || '',
        name: doctor.name,
        specialization: doctor.specialization,
        qualification: doctor.qualification || '',
        experience_years: doctor.experience_years || 0,
        consultation_fee: doctor.consultation_fee || 0
      }
      
      // Load availability
      if (doctor.availability) {
        this.availability = doctor.availability
      } else {
        this.initAvailability()
      }
      
      this.doctorModal.show()
    },
    
    async saveDoctor() {
      try {
        // Prepare availability data
        const availabilityData = {}
        this.weekDays.forEach(day => {
          if (this.availability[day].enabled && this.availability[day].slots.length > 0) {
            // Convert to format expected by backend
            // This will need to be adjusted based on your backend format
            availabilityData[day.toLowerCase()] = this.availability[day].slots
          }
        })
        
        const doctorData = {
          ...this.doctorForm,
          availability: availabilityData
        }
        
        if (this.editingDoctor) {
          await this.$api.updateDoctor(this.editingDoctor.id, doctorData)
        } else {
          await this.$api.addDoctor(doctorData)
        }
        
        this.doctorModal.hide()
        await this.fetchDoctors()
        
      } catch (error) {
        alert(error.response?.data?.error || 'Error saving doctor')
      }
    },
    
    async toggleDoctorStatus(doctor) {
      if (confirm(`Are you sure you want to ${doctor.user?.is_active ? 'deactivate' : 'activate'} ${doctor.name}?`)) {
        try {
          await this.$api.updateDoctor(doctor.id, { is_active: !doctor.user?.is_active })
          await this.fetchDoctors()
        } catch (error) {
          alert('Error updating doctor status')
        }
      }
    },
    
    updateAvailability(day) {
      if (!this.availability[day].enabled) {
        this.availability[day].slots = []
      }
    },
    
    toggleTimeSlot(day, slot) {
      if (!this.availability[day].enabled) return
      
      const index = this.availability[day].slots.indexOf(slot)
      if (index === -1) {
        this.availability[day].slots.push(slot)
        this.availability[day].slots.sort()
      } else {
        this.availability[day].slots.splice(index, 1)
      }
    }
  }
}
</script>