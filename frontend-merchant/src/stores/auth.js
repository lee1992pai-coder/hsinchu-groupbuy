import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('merchant_token') || '')
  const merchantId = ref(localStorage.getItem('merchant_id') || '')

  async function login(email, password) {
    const { data } = await api.post('/auth/merchant/login', { email, password })
    token.value = data.access_token
    localStorage.setItem('merchant_token', data.access_token)
    // 解碼 JWT 取得 merchant id（sub 欄位）
    const payload = JSON.parse(atob(data.access_token.split('.')[1]))
    merchantId.value = payload.sub
    localStorage.setItem('merchant_id', payload.sub)
  }

  function logout() {
    token.value = ''
    merchantId.value = ''
    localStorage.removeItem('merchant_token')
    localStorage.removeItem('merchant_id')
  }

  return { token, merchantId, login, logout }
})
