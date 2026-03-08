<template>
  <div>
    <!-- Page Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>
        <i class="fas fa-history me-2"></i>
        Treatment History
      </h2>
      <button class="btn btn-primary" @click="exportCSV" :disabled="exporting">
        <span v-if="exporting" class="spinner-border spinner-border-sm me-2"></span>
        <i v-else class="fas fa-file-csv me-2"></i>
        Export as CSV
      </button>
    </div>

    <!-- Treatments List -->
    <div class="card">
      <div class="card-body">
        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border mb-3" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p class="text-muted">Loading treatment history...</p>
        </div>
        
        <div v-else-if="treatments.length === 0" class="text-center text-muted py-5">
          <i class="fas fa-notes-medical fa-4x mb-3"></i>
          <h5>No Treatment Records Found</h5>
          <p>Your treatment history will appear here after your first visit.</p>
          <router-link to="/book-appointment" class="btn btn-primary mt-3">
            <i class="fas fa-calendar-plus me-2"></i>
            Book Appointment
          </router-link>
        </div>
        
        <div v-else>
          <div v-for="treatment in treatments" :key="treatment.id" class="card bg-dark mb-3">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-start mb-3">
                <div>
                  <h5 class="card-title mb-1">
                    Dr. {{ treatment.doctor_name }}
                    <small class="text-muted ms-2">{{ treatment.doctor?.specialization || 'Doctor' }}</small>
                  </h5>
                  <p class="text-muted mb-0">
                    <i class="fas fa-calendar-alt me-2"></i>
                    {{ formatDate(treatment.created_at) }}
                  </p>
                </div>
                <span class="badge bg-info">Treatment #{{ treatment.id }}</span>
              </div>
              
              <div class="row">
                <div class="col-md-6">
                  <div class="mb-3">
                    <strong class="text-white-50 d-block mb-2">
                      <i class="fas fa-stethoscope me-2"></i>
                      Diagnosis
                    </strong>
                    <p class="mb-0">{{ treatment.diagnosis }}</p>
                  </div>
                </div>
                
                <div class="col-md-6">
                  <div class="mb-3">
                    <strong class="text-white-50 d-block mb-2">
                      <i class="fas fa-prescription me-2"></i>
                      Prescription
                    </strong>
                    <p class="mb-0">{{ treatment.prescription || 'No prescription' }}</p>
                  </div>
                </div>
              </div>
              
              <div v-if="treatment.notes" class="mb-3">
                <strong class="text-white-50 d-block mb-2">
                  <i class="fas fa-notes-medical me-2"></i>
                  Additional Notes
                </strong>
                <p class="mb-0">{{ treatment.notes }}</p>
              </div>
              
              <div v-if="treatment.next_visit_date" class="mt-3 pt-3 border-top border-secondary">
                <i class="fas fa-calendar-check me-2 text-success"></i>
                <span class="text-success">Next Visit: {{ formatDate(treatment.next_visit_date) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Export Status Modal -->
    <div class="modal fade" id="exportModal" tabindex="-1" ref="exportModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              <i class="fas fa-file-export me-2"></i>
              Export in Progress
            </h5>
          </div>
          <div class="modal-body text-center py-4">
            <div class="spinner-border mb-3" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
            <p>Your CSV file is being generated...</p>
            <p class="text-muted small">You will be notified when it's ready.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TreatmentHistory',
  data() {
    return {
      treatments: [],
      loading: false,
      exporting: false,
      exportModal: null
    }
  },
  mounted() {
    this.fetchTreatments()
    this.exportModal = new bootstrap.Modal(this.$refs.exportModal)
  },
  methods: {
    async fetchTreatments() {
      this.loading = true
      try {
        const response = await this.$api.getTreatmentHistory()
        this.treatments = response.data
      } catch (error) {
        console.error('Error fetching treatments:', error)
      } finally {
        this.loading = false
      }
    },
    
    async exportCSV() {
      this.exporting = true
      this.exportModal.show()
      
      try {
        // This would trigger the async job
        // For now, we'll simulate with a timeout
        await new Promise(resolve => setTimeout(resolve, 2000))
        
        // In real implementation, you would:
        // 1. Call API to start export job
        // 2. Poll for completion
        // 3. Download file when ready
        
        this.exportModal.hide()
        alert('Export completed! Your file will be downloaded shortly.')
        
        // Simulate download
        // window.open('/api/patient/export-csv', '_blank')
        
      } catch (error) {
        this.exportModal.hide()
        alert('Error exporting data')
      } finally {
        this.exporting = false
      }
    },
    
    formatDate(date) {
      return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    }
  }
}
</script>