<template>
  <div class="row justify-content-center">
    <div class="col-md-6 col-lg-4">
      <div class="card">
        <div class="card-header">
          <h4 class="mb-0">
            <i class="fas fa-sign-in-alt me-2"></i>
            Login
          </h4>
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
              {{ loading ? 'Logging in...' : 'Login' }}
            </button>
          </form>

          <hr class="my-4">

          <div class="text-center">
            <p class="text-muted mb-2">Don't have an account?</p>
            <router-link to="/register" class="btn btn-secondary w-100">
              <i class="fas fa-user-plus me-2"></i>
              Register as Patient
            </router-link>
          </div>

          <!-- Demo Credentials -->
          <div class="mt-4 p-3 bg-dark rounded">
            <small class="text-muted d-block mb-2">
              <i class="fas fa-info-circle me-1"></i>
              Demo Credentials:
            </small>
            <div class="row g-2">
              <div class="col-6">
                <div class="p-2 bg-black rounded">
                  <strong class="text-white-50 d-block">Admin</strong>
                  <small class="text-muted">admin / admin123</small>
                </div>
              </div>
              <div class="col-6">
                <div class="p-2 bg-black rounded">
                  <strong class="text-white-50 d-block">Doctor</strong>
                  <small class="text-muted">doctor / doctor123</small>
                </div>
              </div>
              <div class="col-12 mt-2">
                <div class="p-2 bg-black rounded">
                  <strong class="text-white-50 d-block">Patient</strong>
                  <small class="text-muted">patient / patient123</small>
                </div>
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
        
        // FIXED: Redirect based on role instead of emitting event
        const role = userData.user.role
        
        if (role === 'admin') {
          this.$router.push('/admin/dashboard')
        } else if (role === 'doctor') {
          this.$router.push('/doctor/dashboard')
        } else if (role === 'patient') {
          this.$router.push('/patient/dashboard')
        } else {
          // Fallback to home if role is unknown
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