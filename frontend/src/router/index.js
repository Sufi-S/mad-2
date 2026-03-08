import Vue from 'vue'
import VueRouter from 'vue-router'

// Auth components
import Login from '../components/auth/Login.vue'
import Register from '../components/auth/Register.vue'

// Admin components
import AdminDashboard from '../components/admin/AdminDashboard.vue'
import DoctorManagement from '../components/admin/DoctorManagement.vue'

// Doctor components
import DoctorDashboard from '../components/doctor/DoctorDashboard.vue'
import TreatmentForm from '../components/doctor/TreatmentForm.vue'

// Patient components
import PatientDashboard from '../components/patient/PatientDashboard.vue'
import BookAppointment from '../components/patient/BookAppointment.vue'
import TreatmentHistory from '../components/patient/TreatmentHistory.vue'

Vue.use(VueRouter)

const routes = [
  // Public routes
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { guest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { guest: true }
  },
  
  // Admin routes
  {
    path: '/admin/dashboard',
    name: 'AdminDashboard',
    component: AdminDashboard,
    meta: { requiresAuth: true, role: 'admin' }
  },
  {
    path: '/admin/doctors',
    name: 'DoctorManagement',
    component: DoctorManagement,
    meta: { requiresAuth: true, role: 'admin' }
  },
  
  // Doctor routes
  {
    path: '/doctor/dashboard',
    name: 'DoctorDashboard',
    component: DoctorDashboard,
    meta: { requiresAuth: true, role: 'doctor' }
  },
  {
    path: '/doctor/treatment/:appointmentId',
    name: 'TreatmentForm',
    component: TreatmentForm,
    meta: { requiresAuth: true, role: 'doctor' }
  },
  
  // Patient routes
  {
    path: '/patient/dashboard',
    name: 'PatientDashboard',
    component: PatientDashboard,
    meta: { requiresAuth: true, role: 'patient' }
  },
  {
    path: '/doctors',
    name: 'DoctorList',
    component: BookAppointment, // Reusing component for listing
    meta: { requiresAuth: true, role: 'patient' }
  },
  {
    path: '/book-appointment',
    name: 'BookAppointment',
    component: BookAppointment,
    meta: { requiresAuth: true, role: 'patient' }
  },
  {
    path: '/book-appointment/:doctorId',
    name: 'BookAppointmentWithDoctor',
    component: BookAppointment,
    meta: { requiresAuth: true, role: 'patient' }
  },
  {
    path: '/treatment-history',
    name: 'TreatmentHistory',
    component: TreatmentHistory,
    meta: { requiresAuth: true, role: 'patient' }
  },
  
  // Redirect
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '*',
    redirect: '/login'
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  const role = localStorage.getItem('user_role')
  
  // Check if route requires auth
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!token) {
      next('/login')
      return
    }
    
    // Check role if specified
    if (to.meta.role && to.meta.role !== role) {
      // Redirect to appropriate dashboard
      if (role === 'admin') next('/admin/dashboard')
      else if (role === 'doctor') next('/doctor/dashboard')
      else if (role === 'patient') next('/patient/dashboard')
      else next('/login')
      return
    }
  }
  
  // If logged in and trying to access guest routes
  if (to.matched.some(record => record.meta.guest) && token) {
    if (role === 'admin') next('/admin/dashboard')
    else if (role === 'doctor') next('/doctor/dashboard')
    else if (role === 'patient') next('/patient/dashboard')
    else next('/login')
    return
  }
  
  next()
})

export default router