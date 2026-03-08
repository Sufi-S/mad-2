<template>
  <div>
    <!-- Page Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>
        <i class="fas fa-calendar-plus me-2"></i>
        {{ selectedDoctor ? 'Book Appointment' : 'Find Doctors' }}
      </h2>
    </div>

    <!-- Search Section -->
    <div class="card mb-4" v-if="!selectedDoctor">
      <div class="card-header">
        <i class="fas fa-search me-2"></i>
        Search Doctors
      </div>
      <div class="card-body">
        <div class="row">
          <div class="col-md-5">
            <div class="form-group">
              <label class="form-label">Specialization</label>
              <select class="form-select" v-model="searchFilters.specialization">
                <option value="">All Specializations</option>
                <option v-for="dept in departments" :key="dept.id" :value="dept.name">
                  {{ dept.name }}
                </option>
              </select>
            </div>
          </div>
          <div class="col-md-5">
            <div class="form-group">
              <label class="form-label">Doctor Name</label>
              <input 
                type="text" 
                class="form-control" 
                v-model="searchFilters.name"
                placeholder="Search by doctor name"
              >
            </div>
          </div>
          <div class="col-md-2 d-flex align-items-end">
            <button class="btn btn-primary w-100" @click="searchDoctors">
              <i class="fas fa-search me-2"></i>
              Search
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Doctors List -->
    <div class="row" v-if="!selectedDoctor">
      <div class="col-12">
        <div class="card">
          <div class="card-header">
            <i class="fas fa-user-md me-2"></i>
            Available Doctors
          </div>
          <div class="card-body">
            <div v-if="loading" class="text-center py-4">
              <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
            
            <div v-else-if="doctors.length === 0" class="text-center text-muted py-4">
              <i class="fas fa-user-md fa-3x mb-3"></i>
              <p>No doctors found</p>
              <router-link to="/patient/dashboard" class="btn btn-primary">
                <i class="fas fa-arrow-left me-2"></i>
                Back to Dashboard
              </router-link>
            </div>
            
            <div v-else class="row">
              <div v-for="doctor in doctors" :key="doctor.id" class="col-md-6 mb-4">
                <div class="card bg-dark h-100">
                  <div class="card-body">
                    <div class="d-flex align-items-center mb-3">
                      <div class="flex-shrink-0">
                        <i class="fas fa-user-circle fa-3x text-white-50"></i>
                      </div>
                      <div class="flex-grow-1 ms-3">
                        <h5 class="card-title mb-1">{{ doctor.name }}</h5>
                        <p class="text-muted mb-0">{{ doctor.specialization }}</p>
                      </div>
                    </div>
                    
                    <div class="mb-3">
                      <small class="text-white-50 d-block">
                        <i class="fas fa-graduation-cap me-2"></i>
                        {{ doctor.qualification || 'Qualification N/A' }}
                      </small>
                      <small class="text-white-50 d-block">
                        <i class="fas fa-briefcase me-2"></i>
                        {{ doctor.experience_years || 0 }} years experience
                      </small>
                      <small class="text-white-50 d-block">
                        <i class="fas fa-dollar-sign me-2"></i>
                        Consultation Fee: ${{ doctor.consultation_fee || 0 }}
                      </small>
                    </div>
                    
                    <button class="btn btn-primary w-100" @click="selectDoctor(doctor)">
                      <i class="fas fa-calendar-plus me-2"></i>
                      Book Appointment
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Booking Form -->
    <div v-else class="row justify-content-center">
      <div class="col-md-8">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">
              <i class="fas fa-calendar-check me-2"></i>
              Book Appointment with Dr. {{ selectedDoctor.name }}
            </h5>
          </div>
          <div class="card-body">
            <!-- Doctor Info -->
            <div class="mb-4 p-3 bg-dark rounded">
              <div class="row">
                <div class="col-md-6">
                  <p class="mb-1">
                    <strong>Specialization:</strong> {{ selectedDoctor.specialization }}
                  </p>
                  <p class="mb-1">
                    <strong>Experience:</strong> {{ selectedDoctor.experience_years || 0 }} years
                  </p>
                </div>
                <div class="col-md-6">
                  <p class="mb-1">
                    <strong>Qualification:</strong> {{ selectedDoctor.qualification || 'N/A' }}
                  </p>
                  <p class="mb-1">
                    <strong>Fee:</strong> ${{ selectedDoctor.consultation_fee || 0 }}
                  </p>
                </div>
              </div>
            </div>

            <!-- Date Selection -->
            <div class="form-group mb-4">
              <label class="form-label">Select Date</label>
              <div class="row">
                <div class="col-md-4 mb-2" v-for="date in availableDates" :key="date">
                  <button 
                    class="btn w-100" 
                    :class="selectedDate === date ? 'btn-primary' : 'btn-secondary'"
                    @click="selectDate(date)"
                    :disabled="!isDateAvailable(date)"
                  >
                    {{ formatDate(date) }}
                  </button>
                </div>
              </div>
            </div>

            <!-- Time Slots -->
            <div v-if="selectedDate" class="form-group mb-4">
              <label class="form-label">Available Time Slots</label>
              <div class="d-flex flex-wrap gap-2">
                <span 
                  v-for="slot in availableSlots" 
                  :key="slot"
                  class="badge"
                  :class="selectedTime === slot ? 'bg-success' : 'bg-secondary'"
                  @click="selectTime(slot)"
                  style="cursor: pointer; padding: 0.75rem 1.5rem; font-size: 1rem;"
                >
                  {{ slot }}
                </span>
                <div v-if="availableSlots.length === 0" class="text-muted">
                  No available slots for this date
                </div>
              </div>
            </div>

            <!-- Symptoms -->
            <div v-if="selectedTime" class="form-group mb-4">
              <label class="form-label">Symptoms / Reason for Visit</label>
              <textarea 
                class="form-control" 
                rows="3" 
                v-model="symptoms"
                placeholder="Describe your symptoms or reason for visit"
              ></textarea>
            </div>

            <!-- Actions -->
            <div class="d-flex gap-2">
              <button 
                class="btn btn-primary flex-grow-1" 
                :disabled="!selectedTime || booking"
                @click="bookAppointment"
              >
                <span v-if="booking" class="spinner-border spinner-border-sm me-2"></span>
                <i v-else class="fas fa-check me-2"></i>
                Confirm Booking
              </button>
              <button class="btn btn-secondary" @click="selectedDoctor = null">
                <i class="fas fa-arrow-left me-2"></i>
                Back
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'BookAppointment',
  data() {
    return {
      departments: [],
      doctors: [],
      selectedDoctor: null,
      searchFilters: {
        specialization: '',
        name: ''
      },
      loading: false,
      booking: false,
      availableDates: [],
      selectedDate: null,
      availableSlots: [],
      selectedTime: null,
      symptoms: '',
      bookedSlots: {}
    }
  },
  created() {
    this.fetchDepartments()
    
    // Check URL params
    const specialization = this.$route.query.specialization
    if (specialization) {
      this.searchFilters.specialization = specialization
      this.searchDoctors()
    }
  },
  methods: {
    async fetchDepartments() {
      try {
        const response = await this.$api.getDepartments()
        this.departments = response.data
      } catch (error) {
        console.error('Error fetching departments:', error)
      }
    },
    
    async searchDoctors() {
      this.loading = true
      try {
        const response = await this.$api.searchDoctors(
          this.searchFilters.specialization,
          this.searchFilters.name
        )
        this.doctors = response.data
      } catch (error) {
        console.error('Error searching doctors:', error)
      } finally {
        this.loading = false
      }
    },
    
    async selectDoctor(doctor) {
      this.selectedDoctor = doctor
      await this.fetchAvailability()
      this.generateAvailableDates()
    },
    
    async fetchAvailability() {
      try {
        const response = await this.$api.getDoctorAvailability(this.selectedDoctor.id)
        this.bookedSlots = response.data.booked_slots || {}
        
        // Also store doctor's availability schedule
        if (response.data.availability) {
          this.selectedDoctor.availability = response.data.availability
        }
        
        // Generate next 7 days
        this.generateAvailableDates()
        
      } catch (error) {
        console.error('Error fetching availability:', error)
      }
    },
    
    generateAvailableDates() {
      const dates = []
      const today = new Date()
      
      for (let i = 0; i < 7; i++) {
        const date = new Date(today)
        date.setDate(today.getDate() + i)
        const dateStr = date.toISOString().split('T')[0]
        dates.push(dateStr)
      }
      
      this.availableDates = dates
    },
    
    isDateAvailable(date) {
      // Check if doctor has availability for this specific date
      const doctorAvailability = this.selectedDoctor?.availability || {}
      return doctorAvailability[date] && doctorAvailability[date].length > 0
    },
    
    selectDate(date) {
      this.selectedDate = date
      this.selectedTime = null
      
      // FIXED: Use date directly instead of converting to day name
      const doctorAvailability = this.selectedDoctor.availability || {}
      
      // Get doctor's available slots for this specific date
      const availableForDay = doctorAvailability[date] || []
      
      // Remove booked slots
      const bookedForDate = this.bookedSlots[date] || []
      this.availableSlots = availableForDay.filter(slot => !bookedForDate.includes(slot))
    },
    
    selectTime(time) {
      this.selectedTime = time
    },
    
    async bookAppointment() {
      this.booking = true
      try {
        await this.$api.bookAppointment({
          doctor_id: this.selectedDoctor.id,
          date: this.selectedDate,
          time: this.selectedTime,
          symptoms: this.symptoms
        })
        
        alert('Appointment booked successfully!')
        this.$router.push('/patient/dashboard')
        
      } catch (error) {
        alert(error.response?.data?.error || 'Error booking appointment')
      } finally {
        this.booking = false
      }
    },
    
    formatDate(date) {
      return new Date(date).toLocaleDateString('en-US', { 
        weekday: 'short', 
        month: 'short', 
        day: 'numeric' 
      })
    }
  }
}
</script>