import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  async function login(email, password) {
    const { data } = await api.post('/auth/login', { email, password })
    token.value = data.access_token
    localStorage.setItem('token', data.access_token)
    if (data.user) {
      user.value = data.user
      localStorage.setItem('user', JSON.stringify(data.user))
    }
  }

  async function register(payload) {
    const { data } = await api.post('/auth/register', payload)
    token.value = data.access_token
    localStorage.setItem('token', data.access_token)
    if (data.user) {
      user.value = data.user
      localStorage.setItem('user', JSON.stringify(data.user))
    }
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  return { token, user, login, register, logout }
})
