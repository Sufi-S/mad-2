<template>
  <div class="login-container">
    <div class="login-card card">
      <div class="card-header">
        <i class="fas fa-sign-in-alt"></i>
        <h4 class="mb-0">Login</h4>
      </div>
      <div class="card-body">
        <!-- Error Alert -->
        <div v-if="error" class="alert alert-danger">
          <i class="fas fa-exclamation-circle me-2"></i>
          {{ error }}
        </div>

        <!-- Login Form -->
        <form @submit.prevent="handleLogin">
          <div class="form-group">
            <label class="form-label">
              <i class="fas fa-user me-2"></i>
              Username
            </label>
            <input 
              type="text" 
              class="form-control" 
              v-model="credentials.username"
              required
              placeholder="Enter username"
            >
          </div>

          <div class="form-group">
            <label class="form-label">
              <i class="fas fa-lock me-2"></i>
              Password
            </label>
            <input 
              type="password" 
              class="form-control" 
              v-model="credentials.password"
              required
              placeholder="Enter password"
            >
          </div>

          <button type="submit" class="btn btn-primary w-100" :disabled="loading">
            <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
            <i v-else class="fas fa-sign-in-alt me-2"></i>
            {{ loading ? 'Logging in...' : 'LOGIN' }}
          </button>
        </form>

        <hr>

        <div class="text-center">
          <p class="text-muted mb-2">Don't have an account?</p>
          <br>
          <router-link to="/register" class="btn btn-secondary w-100">
            <i class="fas fa-user-plus me-2"></i>
            REGISTER AS PATIENT
          </router-link>
        </div>

        <!-- Demo Credentials -->
        <div class="demo-credentials">
          <small>
            <i class="fas fa-info-circle me-1"></i>
            Demo Credentials:
          </small>
          <div class="row g-2">
            <div class="col-6">
              <div class="credential-item">
                <strong>Admin</strong>
                <small>admin / admin123</small>
              </div>
            </div>
            <div class="col-6">
              <div class="credential-item">
                <strong>Doctor</strong>
                <small>doctor / doctor123</small>
              </div>
            </div>
            <div class="col-12">
              <div class="credential-item">
                <strong>Patient</strong>
                <small>patient / patient123</small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Login',
  data() {
    return {
      credentials: {
        username: '',
        password: ''
      },
      loading: false,
      error: ''
    }
  },
  methods: {
    async handleLogin() {
      this.loading = true
      this.error = ''
      
      try {
        const response = await this.$api.login(this.credentials)
        const userData = response.data
        
        // Store tokens and user data
        localStorage.setItem('access_token', userData.access_token)
        localStorage.setItem('refresh_token', userData.refresh_token)
        localStorage.setItem('user_role', userData.user.role)
        localStorage.setItem('user', JSON.stringify(userData.user))
        
        if (userData.profile) {
          localStorage.setItem('profile', JSON.stringify(userData.profile))
        }
        
        // Redirect based on role
        const role = userData.user.role
        
        if (role === 'admin') {
          this.$router.push('/admin/dashboard')
        } else if (role === 'doctor') {
          this.$router.push('/doctor/dashboard')
        } else if (role === 'patient') {
          this.$router.push('/patient/dashboard')
        } else {
          this.$router.push('/')
        }
        
      } catch (error) {
        this.error = error.response?.data?.error || 'Login failed. Please try again.'
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
/* Add any component-specific styles here if needed */
</style>