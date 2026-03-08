<template>
  <div id="app">
    <!-- Navigation Bar -->
    <nav class="navbar navbar-expand-lg navbar-dark" v-if="isLoggedIn">
      <div class="container">
        <router-link class="navbar-brand" to="/">
          <i class="fas fa-hospital me-2"></i>
          HMS
        </router-link>
        
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
          <span class="navbar-toggler-icon"></span>
        </button>
        
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav ms-auto">
            <!-- Admin Navigation -->
            <template v-if="userRole === 'admin'">
              <li class="nav-item">
                <router-link class="nav-link" to="/admin/dashboard">
                  <i class="fas fa-tachometer-alt me-1"></i> Dashboard
                </router-link>
              </li>
            </template>

            <!-- Doctor Navigation -->
            <template v-if="userRole === 'doctor'">
              <li class="nav-item">
                <router-link class="nav-link" to="/doctor/dashboard">
                  <i class="fas fa-tachometer-alt me-1"></i> Dashboard
                </router-link>
              </li>
            </template>

            <!-- Patient Navigation -->
            <template v-if="userRole === 'patient'">
              <li class="nav-item">
                <router-link class="nav-link" to="/patient/dashboard">
                  <i class="fas fa-tachometer-alt me-1"></i> Dashboard
                </router-link>
              </li>
              <li class="nav-item">
                <router-link class="nav-link" to="/doctors">
                  <i class="fas fa-user-md me-1"></i> Find Doctors
                </router-link>
              </li>
              <li class="nav-item">
                <router-link class="nav-link" to="/book-appointment">
                  <i class="fas fa-calendar-plus me-1"></i> Book Appointment
                </router-link>
              </li>
              <li class="nav-item">
                <router-link class="nav-link" to="/treatment-history">
                  <i class="fas fa-history me-1"></i> My History
                </router-link>
              </li>
            </template>

            <!-- User Info & Logout -->
            <li class="nav-item dropdown">
              <a class="nav-link dropdown-toggle" href="#" id="userDropdown" role="button" data-bs-toggle="dropdown">
                <i class="fas fa-user-circle me-1"></i>
                {{ username || 'User' }}
              </a>
              <ul class="dropdown-menu dropdown-menu-end">
                <li>
                  <span class="dropdown-item-text text-muted">
                    Role: {{ userRole | capitalize }}
                  </span>
                </li>
                <li><hr class="dropdown-divider"></li>
                <li>
                  <a class="dropdown-item" href="#" @click.prevent="logout">
                    <i class="fas fa-sign-out-alt me-2"></i> Logout
                  </a>
                </li>
              </ul>
            </li>
          </ul>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <div class="container mt-4">
      <router-view @auth-success="handleAuthSuccess" />
    </div>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      isLoggedIn: false,
      userRole: null,
      username: null
    }
  },
  created() {
    this.checkAuth()
  },
  methods: {
    checkAuth() {
      const token = localStorage.getItem('access_token')
      const role = localStorage.getItem('user_role')
      const user = localStorage.getItem('user')
      
      this.isLoggedIn = !!token
      this.userRole = role
      
      if (user) {
        const userData = JSON.parse(user)
        this.username = userData.username
      }
    },
    handleAuthSuccess(userData) {
      this.isLoggedIn = true
      this.userRole = userData.user.role
      this.username = userData.user.username
      
      // Redirect based on role
      if (this.userRole === 'admin') {
        this.$router.push('/admin/dashboard')
      } else if (this.userRole === 'doctor') {
        this.$router.push('/doctor/dashboard')
      } else {
        this.$router.push('/patient/dashboard')
      }
    },
    async logout() {
      try {
        await this.$api.logout()
      } finally {
        localStorage.clear()
        this.isLoggedIn = false
        this.userRole = null
        this.username = null
        this.$router.push('/login')
      }
    }
  },
  filters: {
    capitalize(value) {
      if (!value) return ''
      return value.charAt(0).toUpperCase() + value.slice(1)
    }
  }
}
</script>

<style>
@import './assets/styles.css';
</style>