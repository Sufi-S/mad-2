import Vue from 'vue'
import VueRouter from 'vue-router'

// Auth components
import Login from '../components/auth/Login.vue'
import Register from '../components/auth/Register.vue'

// Layout components
import AdminDashboard from '../components/admin/AdminDashboard.vue' // This already has layout
import DoctorLayout from '../components/doctor/DoctorLayout.vue'
import PatientLayout from '../components/patient/PatientLayout.vue'

// Content components
import DoctorManagement from '../components/admin/DoctorManagement.vue'
import DoctorDashboard from '../components/doctor/DoctorDashboard.vue'
import TreatmentForm from '../components/doctor/TreatmentForm.vue'
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
  
  // Admin routes - AdminDashboard already has layout
  {
    path: '/admin',
    component: AdminDashboard,
    meta: { requiresAuth: true, role: 'admin' },
    children: [
      {
        path: '',
        redirect: '/admin/dashboard'
      },
      {
        path: 'dashboard',
        name: 'AdminDashboard',
        component: AdminDashboard
      },
      {
        path: 'doctors',
        name: 'DoctorManagement',
        component: DoctorManagement
      }
    ]
  },
  
  // Doctor routes - using DoctorLayout
  {
    path: '/doctor',
    component: DoctorLayout,
    meta: { requiresAuth: true, role: 'doctor' },
    children: [
      {
        path: '',
        redirect: '/doctor/dashboard'
      },
      {
        path: 'dashboard',
        name: 'DoctorDashboard',
        component: DoctorDashboard
      },
      {
        path: 'treatment/:appointmentId?',
        name: 'TreatmentForm',
        component: TreatmentForm
      }
    ]
  },
  
  // Patient routes - using PatientLayout
  {
    path: '/patient',
    component: PatientLayout,
    meta: { requiresAuth: true, role: 'patient' },
    children: [
      {
        path: '',
        redirect: '/patient/dashboard'
      },
      {
        path: 'dashboard',
        name: 'PatientDashboard',
        component: PatientDashboard
      },
      {
        path: 'book-appointment',
        name: 'BookAppointment',
        component: BookAppointment
      },
      {
        path: 'book-appointment/:doctorId',
        name: 'BookAppointmentWithDoctor',
        component: BookAppointment
      },
      {
        path: 'treatment-history',
        name: 'TreatmentHistory',
        component: TreatmentHistory
      },
      {
        path: 'doctors',
        name: 'DoctorList',
        component: BookAppointment
      }
    ]
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