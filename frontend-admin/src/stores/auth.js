import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api'

export const useAdminAuthStore = defineStore('adminAuth', () => {
  const token = ref(localStorage.getItem('admin_token') || '')
  const admin = ref(JSON.parse(localStorage.getItem('admin_user') || 'null'))

  const isLoggedIn = computed(() => !!token.value)

  async function login(email, password) {
    const { data } = await api.post('/auth/admin/login', { email, password })
    token.value = data.access_token
    admin.value = data.user || null
    localStorage.setItem('admin_token', data.access_token)
    if (data.user) localStorage.setItem('admin_user', JSON.stringify(data.user))
  }

  function logout() {
    token.value = ''
    admin.value = null
    localStorage.removeItem('admin_token')
    localStorage.removeItem('admin_user')
  }

  return { token, admin, isLoggedIn, login, logout }
})
