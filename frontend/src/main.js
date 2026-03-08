import Vue from 'vue'
import App from './App.vue'
import router from './router'
import api from './api'

import * as bootstrap from 'bootstrap'

Vue.config.productionTip = false

// Make API available globally
Vue.prototype.$api = api

// Check authentication on app start
const token = localStorage.getItem('access_token')
if (token) {
  // You could verify token here
}

new Vue({
  router,
  render: h => h(App)
}).$mount('#app')