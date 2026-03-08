<template>
  <div class="admin-layout">
    <!-- Sidebar -->
    <div class="sidebar">
      <div class="sidebar-header">
        <h3>Admin Panel</h3>
      </div>
      <ul class="nav flex-column">
        <li class="nav-item">
          <router-link to="/admin/dashboard" class="nav-link" active-class="active">
            <i class="fas fa-tachometer-alt me-2"></i>
            Dashboard
          </router-link>
        </li>
        <li class="nav-item">
          <router-link to="/admin/doctors" class="nav-link" active-class="active">
            <i class="fas fa-user-md me-2"></i>
            Manage Doctors
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

    <!-- Delete Confirmation Modal -->
    <div class="modal fade" id="deleteModal" tabindex="-1" ref="deleteModal">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">
              <i class="fas fa-exclamation-triangle text-danger me-2"></i>
              Confirm Delete
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            Are you sure you want to delete {{ deleteTarget?.name }}?
            <p class="text-muted mt-2">
              <small>This will deactivate the user account. This action can be undone by reactivating.</small>
            </p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button type="button" class="btn btn-danger" @click="deleteConfirmed">
              <i class="fas fa-trash me-2"></i>
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AdminDashboard',
  data() {
    return {
      stats: {},
      appointments: [],
      searchQuery: '',
      searchType: 'all',
      searchResults: null,
      showSearch: false,
      loading: false,
      deleteTarget: null
    }
  },
  mounted() {
    this.fetchData()
    if (this.$refs.deleteModal) {
      this.deleteModal = new bootstrap.Modal(this.$refs.deleteModal)
    }
  },
  methods: {
    async fetchData() {
      this.loading = true
      try {
        const [dashboard, appointments] = await Promise.all([
          this.$api.getAdminDashboard(),
          this.$api.getAllAppointments()
        ])
        
        this.stats = dashboard.data
        this.appointments = appointments.data.slice(0, 10) // Last 10 appointments
        
      } catch (error) {
        console.error('Error fetching data:', error)
      } finally {
        this.loading = false
      }
    },
    
    async refreshData() {
      await this.fetchData()
    },
    
    async performSearch() {
      if (!this.searchQuery.trim()) {
        this.searchResults = null
        return
      }
      
      try {
        const response = await this.$api.search(this.searchQuery, this.searchType)
        this.searchResults = response.data
      } catch (error) {
        console.error('Search error:', error)
      }
    },
    
    confirmDeletePatient(patient) {
      this.deleteTarget = { type: 'patient', id: patient.id, name: patient.name }
      this.deleteModal.show()
    },
    
    async deleteConfirmed() {
      try {
        if (this.deleteTarget.type === 'patient') {
          await this.$api.deletePatient(this.deleteTarget.id)
        }
        
        this.deleteModal.hide()
        this.searchResults = null
        this.searchQuery = ''
        await this.fetchData()
        
      } catch (error) {
        alert('Error deleting user')
      }
    },
    
    formatDate(date) {
      return new Date(date).toLocaleDateString()
    },
    
    exportReport() {
      // TODO: Implement report export
      alert('Report export feature coming soon!')
    },
    
    logout() {
      localStorage.clear()
      this.$router.push('/login')
    }
  }
}
</script>

<style scoped>
.admin-layout {
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
  
  .admin-layout {
    flex-direction: column;
  }
}
</style>