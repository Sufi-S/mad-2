<template>
  <div>
    <!-- Page Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>
        <i class="fas fa-tachometer-alt me-2"></i>
        Doctor Dashboard
      </h2>
      <div>
        <button class="btn btn-primary me-2" @click="refreshData">
          <i class="fas fa-sync-alt me-2"></i>
          Refresh
        </button>
        <button class="btn btn-secondary" @click="showAvailabilityModal = true">
          <i class="fas fa-clock me-2"></i>
          Set Availability
        </button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="row mb-4">
      <div class="col-md-4 mb-3">
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-calendar-day"></i>
          </div>
          <div class="stat-value">{{ todayAppointments }}</div>
          <div class="stat-label">Today's Appointments</div>
        </div>
      </div>
      <div class="col-md-4 mb-3">
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-users"></i>
          </div>
          <div class="stat-value">{{ totalPatients }}</div>
          <div class="stat-label">Total Patients</div>
        </div>
      </div>
      <div class="col-md-4 mb-3">
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fas fa-check-circle"></i>
          </div>
          <div class="stat-value">{{ completedAppointments }}</div>
          <div class="stat-label">Completed</div>
        </div>
      </div>
    </div>

    <!-- Today's Appointments -->
    <div class="card mb-4">
      <div class="card-header">
        <i class="fas fa-calendar-day me-2"></i>
        Today's Appointments
      </div>
      <div class="card-body">
        <div v-if="todayAppointmentsList.length === 0" class="text-center text-muted py-4">
          <i class="fas fa-calendar-check fa-3x mb-3"></i>
          <p>No appointments scheduled for today</p>
        </div>
        
        <div v-else class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>Time</th>
                <th>Patient</th>
                <th>Phone</th>
                <th>Symptoms</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="apt in todayAppointmentsList" :key="apt.id">
                <td>{{ apt.appointment_time }}</td>
                <td>
                  <strong>{{ apt.patient_name }}</strong>
                </td>
                <td>{{ apt.patient?.phone || 'N/A' }}</td>
                <td>{{ apt.symptoms || 'N/A' }}</td>
                <td>
                  <span class="badge" :class="{
                    'bg-warning': apt.status === 'booked',
                    'bg-success': apt.status === 'completed',
                    'bg-danger': apt.status === 'cancelled'
                  }">
                    {{ apt.status }}
                  </span>
                </td>
                <td>
                  <button v-if="apt.status === 'booked'" 
                          class="btn btn-sm btn-success me-1"
                          @click="startTreatment(apt)">
                    <i class="fas fa-stethoscope me-1"></i>
                    Start
                  </button>
                  <button v-if="apt.status === 'booked'" 
                          class="btn btn-sm btn-danger"
                          @click="cancelAppointment(apt)">
                    <i class="fas fa-times me-1"></i>
                    Cancel
                  </button>
                  <span v-if="apt.status === 'completed'" class="text-success">
                    <i class="fas fa-check-circle me-1"></i>
                    Completed
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Upcoming Appointments -->
    <div class="card">
      <div class="card-header">
        <i class="fas fa-calendar-week me-2"></i>
        Upcoming Appointments
      </div>
      <div class="card-body">
        <div v-if="upcomingAppointments.length === 0" class="text-center text-muted py-4">
          <i class="fas fa-calendar-plus fa-3x mb-3"></i>
          <p>No upcoming appointments</p>
        </div>
        
        <div v-else class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>Date</th>
                <th>Time</th>
                <th>Patient</th>
                <th>Phone</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="apt in upcomingAppointments" :key="apt.id">
                <td>{{ formatDate(apt.appointment_date) }}</td>
                <td>{{ apt.appointment_time }}</td>
                <td>{{ apt.patient_name }}</td>
                <td>{{ apt.patient?.phone || 'N/A' }}</td>
                <td>
                  <span class="badge bg-warning">Scheduled</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Set Availability Modal -->
    <div class="modal fade" id="availabilityModal" tabindex="-1" ref="availabilityModal">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              <i class="fas fa-clock me-2"></i>
              Set Weekly Availability
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <div class="row">
              <div class="col-12">
                <div class="table-responsive">
                  <table class="table">
                    <thead>
                      <tr>
                        <th>Day</th>
                        <th>Available</th>
                        <th>Time Slots</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="day in weekDays" :key="day">
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
                              v-for="slot in timeSlots" 
                              :key="slot"
                              class="badge"
                              :class="availability[day].slots.includes(slot) ? 'bg-success' : 'bg-secondary'"
                              @click="toggleTimeSlot(day, slot)"
                              style="cursor: pointer;"
                            >
                              {{ slot }}
                            </span>
                          </div>
                          <span v-else class="text-muted">Not available</span>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-primary" @click="saveAvailability">
              Save Availability
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DoctorDashboard',
  data() {
    return {
      todayAppointments: 0,
      totalPatients: 0,
      completedAppointments: 0,
      todayAppointmentsList: [],
      upcomingAppointments: [],
      availability: {},
      weekDays: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
      timeSlots: ['09:00', '10:00', '11:00', '14:00', '15:00', '16:00'],
      showAvailabilityModal: false
    }
  },
  mounted() {
    this.fetchDashboard()
    this.fetchAvailability()
    this.availabilityModal = new bootstrap.Modal(this.$refs.availabilityModal)
  },
  watch: {
    showAvailabilityModal(val) {
      if (val) {
        this.availabilityModal.show()
      } else {
        this.availabilityModal.hide()
      }
    }
  },
  methods: {
    async fetchDashboard() {
      try {
        const response = await this.$api.getDoctorDashboard()
        const data = response.data
        
        this.todayAppointments = data.today_appointments || 0
        this.totalPatients = data.total_patients || 0
        this.completedAppointments = data.completed_appointments || 0
        this.todayAppointmentsList = data.today_appointments_list || []
        this.upcomingAppointments = data.upcoming_appointments || []
        
      } catch (error) {
        console.error('Error fetching dashboard:', error)
      }
    },
    
    async fetchAvailability() {
      try {
        const response = await this.$api.getAvailability()
        const savedAvailability = response.data.availability || {}
        
        // Initialize availability structure
        this.weekDays.forEach(day => {
          this.availability[day] = {
            enabled: !!savedAvailability[day.toLowerCase()],
            slots: savedAvailability[day.toLowerCase()] || []
          }
        })
        
      } catch (error) {
        console.error('Error fetching availability:', error)
      }
    },
    
    async refreshData() {
      await this.fetchDashboard()
    },
    
    startTreatment(appointment) {
      this.$router.push(`/doctor/treatment/${appointment.id}`)
    },
    
    async cancelAppointment(appointment) {
      if (confirm(`Cancel appointment with ${appointment.patient_name}?`)) {
        try {
          await this.$api.updateAppointmentStatus(appointment.id, 'cancelled')
          await this.fetchDashboard()
        } catch (error) {
          alert('Error cancelling appointment')
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
    },
    
    async saveAvailability() {
      try {
        // Format availability for backend
        const availabilityData = {}
        this.weekDays.forEach(day => {
          if (this.availability[day].enabled && this.availability[day].slots.length > 0) {
            availabilityData[day.toLowerCase()] = this.availability[day].slots
          }
        })
        
        await this.$api.updateAvailability(availabilityData)
        this.showAvailabilityModal = false
        alert('Availability updated successfully!')
        
      } catch (error) {
        alert('Error saving availability')
      }
    },
    
    formatDate(date) {
      return new Date(date).toLocaleDateString()
    }
  }
}
</script>
