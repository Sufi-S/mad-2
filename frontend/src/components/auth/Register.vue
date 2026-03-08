<template>
  <div class="row justify-content-center">
    <div class="col-md-8 col-lg-6">
      <div class="card">
        <div class="card-header">
          <h4 class="mb-0">
            <i class="fas fa-user-plus me-2"></i>
            Patient Registration
          </h4>
        </div>
        <div class="card-body">
          <!-- Success/Error Alerts -->
          <div v-if="success" class="alert alert-success">
            <i class="fas fa-check-circle me-2"></i>
            {{ success }}
          </div>
          
          <div v-if="error" class="alert alert-danger">
            <i class="fas fa-exclamation-circle me-2"></i>
            {{ error }}
          </div>

          <form @submit.prevent="handleRegister">
            <!-- Account Information -->
            <h5 class="text-white-50 mb-3">
              <i class="fas fa-id-card me-2"></i>
              Account Information
            </h5>
            
            <div class="row">
              <div class="col-md-6 mb-3">
                <label class="form-label">Username *</label>
                <input 
                  type="text" 
                  class="form-control" 
                  v-model="formData.username"
                  required
                  placeholder="Choose username"
                >
              </div>
              <div class="col-md-6 mb-3">
                <label class="form-label">Email *</label>
                <input 
                  type="email" 
                  class="form-control" 
                  v-model="formData.email"
                  required
                  placeholder="Enter email"
                >
              </div>
            </div>

            <div class="row">
              <div class="col-md-6 mb-3">
                <label class="form-label">Password *</label>
                <input 
                  type="password" 
                  class="form-control" 
                  v-model="formData.password"
                  required
                  minlength="6"
                  placeholder="Min 6 characters"
                >
              </div>
              <div class="col-md-6 mb-4">
                <label class="form-label">Confirm Password *</label>
                <input 
                  type="password" 
                  class="form-control" 
                  v-model="confirmPassword"
                  required
                  placeholder="Re-enter password"
                >
              </div>
            </div>

            <!-- Personal Information -->
            <h5 class="text-white-50 mb-3">
              <i class="fas fa-user me-2"></i>
              Personal Information
            </h5>

            <div class="row">
              <div class="col-md-6 mb-3">
                <label class="form-label">Full Name *</label>
                <input 
                  type="text" 
                  class="form-control" 
                  v-model="formData.name"
                  required
                  placeholder="Enter full name"
                >
              </div>
              <div class="col-md-6 mb-3">
                <label class="form-label">Phone Number *</label>
                <input 
                  type="tel" 
                  class="form-control" 
                  v-model="formData.phone"
                  required
                  placeholder="Enter phone number"
                >
              </div>
            </div>

            <div class="row">
              <div class="col-md-6 mb-3">
                <label class="form-label">Date of Birth</label>
                <input 
                  type="date" 
                  class="form-control" 
                  v-model="formData.date_of_birth"
                >
              </div>
              <div class="col-md-6 mb-3">
                <label class="form-label">Gender</label>
                <select class="form-select" v-model="formData.gender">
                  <option value="">Select Gender</option>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="other">Other</option>
                </select>
              </div>
            </div>

            <div class="row">
              <div class="col-md-6 mb-3">
                <label class="form-label">Blood Group</label>
                <select class="form-select" v-model="formData.blood_group">
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
              <div class="col-md-6 mb-3">
                <label class="form-label">Emergency Contact</label>
                <input 
                  type="tel" 
                  class="form-control" 
                  v-model="formData.emergency_contact"
                  placeholder="Emergency phone number"
                >
              </div>
            </div>

            <div class="mb-4">
              <label class="form-label">Address</label>
              <textarea 
                class="form-control" 
                rows="2" 
                v-model="formData.address"
                placeholder="Enter full address"
              ></textarea>
            </div>

            <div class="d-flex gap-2">
              <button type="submit" class="btn btn-primary flex-grow-1" :disabled="loading">
                <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                <i v-else class="fas fa-user-plus me-2"></i>
                {{ loading ? 'Registering...' : 'Register' }}
              </button>
              <router-link to="/login" class="btn btn-secondary">
                <i class="fas fa-arrow-left me-2"></i>
                Back
              </router-link>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Register',
  data() {
    return {
      formData: {
        username: '',
        email: '',
        password: '',
        name: '',
        phone: '',
        date_of_birth: '',
        gender: '',
        address: '',
        blood_group: '',
        emergency_contact: ''
      },
      confirmPassword: '',
      loading: false,
      error: '',
      success: ''
    }
  },
  methods: {
    async handleRegister() {
      // Validate passwords match
      if (this.formData.password !== this.confirmPassword) {
        this.error = 'Passwords do not match'
        return
      }
      
      this.loading = true
      this.error = ''
      this.success = ''
      
      try {
        await this.$api.register(this.formData)
        this.success = 'Registration successful! Redirecting to login...'
        
        // Clear form
        this.formData = {
          username: '', email: '', password: '', name: '',
          phone: '', date_of_birth: '', gender: '',
          address: '', blood_group: '', emergency_contact: ''
        }
        this.confirmPassword = ''
        
        // Redirect to login after 2 seconds
        setTimeout(() => {
          this.$router.push('/login')
        }, 2000)
        
      } catch (error) {
        this.error = error.response?.data?.error || 'Registration failed. Please try again.'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>