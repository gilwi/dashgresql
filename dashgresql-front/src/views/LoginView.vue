<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

const username = ref('')
const password = ref('')
const isLoading = ref(false)
const error = ref('')

const handleLogin = async () => {
  error.value = ''
  isLoading.value = true
  try {
    await auth.login(username.value, password.value)
    router.push('/')
  } catch (err) {
    error.value = err.response?.data?.error ?? 'Authentication failed'
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen w-full bg-surface flex items-center justify-center p-6">
    <div
      class="w-full max-w-md bg-surface-container-lowest/70 backdrop-blur-xl p-12 rounded-3xl shadow-ambient"
    >
      <header class="mb-10 text-center">
        <h1 class="text-display-sm font-bold tracking-tighter text-primary mb-2">dashgresql</h1>
        <p class="text-on-surface-variant text-sm uppercase tracking-widest">The Data Architect</p>
      </header>
      <form @submit.prevent="handleLogin" class="space-y-8">
        <div class="space-y-2">
          <label class="text-label-md text-on-surface-variant px-1">Architect Username</label>
          <input
            v-model="username"
            type="text"
            placeholder="e.g. postgres_admin"
            class="w-full h-12 px-4 bg-surface-container-lowest rounded-md outline-1 outline-outline-variant/20 focus:outline-primary focus:ring-4 focus:ring-primary/10 transition-all placeholder:text-surface-dim"
            required
          />
        </div>
        <div class="space-y-2">
          <label class="text-label-md text-on-surface-variant px-1">Access Key</label>
          <input
            v-model="password"
            type="password"
            placeholder="••••••••"
            class="w-full h-12 px-4 bg-surface-container-lowest rounded-md outline-1 outline-outline-variant/20 focus:outline-primary focus:ring-4 focus:ring-primary/10 transition-all placeholder:text-surface-dim"
            required
          />
        </div>

        <!-- Error message -->
        <p v-if="error" class="text-sm text-red-400 text-center -mt-4">
          {{ error }}
        </p>

        <button
          type="submit"
          :disabled="isLoading"
          class="w-full h-12 bg-primary text-on-primary font-bold rounded-md shadow-ambient hover:scale-[1.02] active:scale-95 transition-transform disabled:opacity-50"
        >
          {{ isLoading ? 'Authenticating...' : 'Enter Workspace' }}
        </button>
      </form>
      <footer class="mt-12 text-center">
        <p class="text-label-md text-outline-variant uppercase tracking-tighter">
          Secure Session • PostgreSQL 16+
        </p>
      </footer>
    </div>
  </div>
</template>
