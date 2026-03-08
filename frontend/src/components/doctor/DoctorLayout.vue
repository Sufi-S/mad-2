<template>
  <div class="doctor-layout">
    <!-- Sidebar -->
    <div class="sidebar">
      <div class="sidebar-header">
        <h3>Doctor Panel</h3>
      </div>
      <ul class="nav flex-column">
        <li class="nav-item">
          <router-link to="/doctor/dashboard" class="nav-link" active-class="active">
            <i class="fas fa-tachometer-alt me-2"></i>
            Dashboard
          </router-link>
        </li>
        <li class="nav-item">
          <a href="#" class="nav-link" @click.prevent="logout">
            <i class="fas fa-sign-out-alt me-2"></i>
            Logout
          </a>
        </li>
      </ul>
    </div>

    <!-- Main Content -->
    <div class="main-content">
      <router-view></router-view>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DoctorLayout',
  methods: {
    logout() {
      localStorage.clear()
      this.$router.push('/login')
    }
  }
}
</script>

<style scoped>
.doctor-layout {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  width: 250px;
  background-color: var(--bg-secondary);
  border-right: 1px solid var(--border-color);
  padding: 2rem 0;
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  overflow-y: auto;
}

.sidebar-header {
  padding: 0 1.5rem;
  margin-bottom: 2rem;
}

.sidebar-header h3 {
  color: var(--text-primary);
  font-size: 1.5rem;
  margin: 0;
}

.nav {
  list-style: none;
  padding: 0;
  margin: 0;
}

.nav-item {
  margin-bottom: 0.5rem;
}

.nav-link {
  display: block;
  padding: 0.75rem 1.5rem;
  color: var(--text-secondary);
  text-decoration: none;
  transition: all 0.3s ease;
  border-left: 3px solid transparent;
}

.nav-link:hover {
  background-color: var(--bg-hover);
  color: var(--text-primary);
}

.nav-link.active {
  background-color: var(--bg-hover);
  color: var(--text-primary);
  border-left-color: var(--text-primary);
}

.nav-link i {
  width: 20px;
}

.main-content {
  flex: 1;
  margin-left: 250px;
  padding: 2rem;
  background-color: var(--bg-primary);
  min-height: 100vh;
}

@media (max-width: 768px) {
  .sidebar {
    width: 100%;
    position: relative;
    height: auto;
  }
  
  .main-content {
    margin-left: 0;
    padding: 1rem;
  }
  
  .doctor-layout {
    flex-direction: column;
  }
}
</style>