<template>
  <div>
    <div class="row justify-content-center">
      <div class="col-md-8">
        <div class="card">
          <div class="card-header">
            <h4 class="mb-0">
              <i class="fas fa-stethoscope me-2"></i>
              Treatment Form
            </h4>
          </div>
          <div class="card-body">
            <!-- Appointment Info -->
            <div class="mb-4 p-3 bg-dark rounded">
              <h6 class="text-white-50 mb-3">Appointment Details</h6>
              <div class="row">
                <div class="col-md-6">
                  <p class="mb-1">
                    <strong>Patient:</strong> {{ appointment.patient_name }}
                  </p>
                  <p class="mb-1">
                    <strong>Date:</strong> {{ formatDate(appointment.appointment_date) }}
                  </p>
                </div>
                <div class="col-md-6">
                  <p class="mb-1">
                    <strong>Time:</strong> {{ appointment.appointment_time }}
                  </p>
                  <p class="mb-1">
                    <strong>Symptoms:</strong> {{ appointment.symptoms || 'N/A' }}
                  </p>
                </div>
              </div>
            </div>

            <!-- Treatment Form -->
            <form @submit.prevent="saveTreatment">
              <div class="form-group mb-3">
                <label class="form-label">
                  <i class="fas fa-diagnoses me-2"></i>
                  Diagnosis *
                </label>
                <textarea 
                  class="form-control" 
                  rows="3" 
                  v-model="treatment.diagnosis"
                  required
                  placeholder="Enter diagnosis"
                ></textarea>
              </div>

              <div class="form-group mb-3">
                <label class="form-label">
                  <i class="fas fa-prescription me-2"></i>
                  Prescription
                </label>
                <textarea 
                  class="form-control" 
                  rows="3" 
                  v-model="treatment.prescription"
                  placeholder="Enter prescription"
                ></textarea>
              </div>

              <div class="form-group mb-3">
                <label class="form-label">
                  <i class="fas fa-notes-medical me-2"></i>
                  Additional Notes
                </label>
                <textarea 
                  class="form-control" 
                  rows="2" 
                  v-model="treatment.notes"
                  placeholder="Any additional notes"
                ></textarea>
              </div>

              <div class="form-group mb-4">
                <label class="form-label">
                  <i class="fas fa-calendar-check me-2"></i>
                  Next Visit Date
                </label>
                <input 
                  type="date" 
                  class="form-control" 
                  v-model="treatment.next_visit_date"
                  :min="minNextVisitDate"
                >
                <small class="text-muted">Leave empty if not required</small>
              </div>

              <div class="d-flex gap-2">
                <button type="submit" class="btn btn-primary flex-grow-1" :disabled="saving">
                  <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
                  <i v-else class="fas fa-save me-2"></i>
                  {{ saving ? 'Saving...' : 'Save Treatment' }}
                </button>
                <button type="button" class="btn btn-secondary" @click="goBack">
                  <i class="fas fa-arrow-left me-2"></i>
                  Back
                </button>
              </div>
            </form>
          </div>
        </div>

        <!-- Patient History -->
        <div class="card mt-4" v-if="patientHistory.length > 0">
          <div class="card-header">
            <i class="fas fa-history me-2"></i>
            Patient History
          </div>
          <div class="card-body">
            <div class="table-responsive">
              <table class="table table-hover">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Diagnosis</th>
                    <th>Prescription</th>
                    <th>Next Visit</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="record in patientHistory" :key="record.id">
                    <td>{{ formatDate(record.created_at) }}</td>
                    <td>{{ record.diagnosis }}</td>
                    <td>{{ record.prescription || 'N/A' }}</td>
                    <td>{{ record.next_visit_date ? formatDate(record.next_visit_date) : 'N/A' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TreatmentForm',
  data() {
    return {
      appointmentId: null,
      appointment: {},
      treatment: {
        diagnosis: '',
        prescription: '',
        notes: '',
        next_visit_date: ''
      },
      patientHistory: [],
      saving: false,
      minNextVisitDate: new Date().toISOString().split('T')[0]
    }
  },
  created() {
    this.appointmentId = this.$route.params.appointmentId
    this.fetchAppointment()
    this.fetchPatientHistory()
  },
  methods: {
    async fetchAppointment() {
      try {
        // Get appointment details from the appointments list
        const response = await this.$api.getDoctorAppointments('booked')
        this.appointment = response.data.find(apt => apt.id == this.appointmentId) || {}
        
        if (!this.appointment.id) {
          alert('Appointment not found')
          this.goBack()
        }
      } catch (error) {
        console.error('Error fetching appointment:', error)
      }
    },
    
    async fetchPatientHistory() {
      if (!this.appointment.patient_id) return
      
      try {
        const response = await this.$api.getPatientHistory(this.appointment.patient_id)
        this.patientHistory = response.data.treatments || []
      } catch (error) {
        console.error('Error fetching patient history:', error)
      }
    },
    
    async saveTreatment() {
      this.saving = true
      try {
        await this.$api.saveTreatment(this.appointmentId, this.treatment)
        
        // Update appointment status
        await this.$api.updateAppointmentStatus(this.appointmentId, 'completed')
        
        alert('Treatment saved successfully!')
        this.$router.push('/doctor/dashboard')
        
      } catch (error) {
        alert(error.response?.data?.error || 'Error saving treatment')
      } finally {
        this.saving = false
      }
    },
    
    goBack() {
      this.$router.push('/doctor/dashboard')
    },
    
    formatDate(date) {
      return new Date(date).toLocaleDateString()
    }
  }
}
</script>