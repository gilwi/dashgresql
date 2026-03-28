import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(sessionStorage.getItem('access_token') ?? null)
  const user = ref(null)

  const isAuthenticated = computed(() => !!token.value)

  async function login(username, password) {
    const res = await api.post('/api/auth/login', { username, password })
    token.value = res.data.access_token
    sessionStorage.setItem('access_token', token.value)
    await fetchUser()
  }

  async function fetchUser() {
    const res = await api.get('/api/auth/me')
    user.value = res.data
  }

  async function logout() {
    await api.post('/api/auth/logout').catch(() => {}) // best effort
    token.value = null
    user.value = null
    sessionStorage.removeItem('access_token')
  }

  return { token, user, isAuthenticated, login, fetchUser, logout }
})
