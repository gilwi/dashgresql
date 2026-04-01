<script setup>
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()

const handleLogout = async () => {
  await auth.logout()
  router.push({ name: 'login' })
}
</script>

<template>
  <header
    class="h-16 sticky top-0 z-40 bg-surface-container-low flex justify-between items-center px-8"
  >
    <!-- Left slot — reserved for future search bar or breadcrumb -->
    <div class="flex items-center gap-8">
      <slot name="left" />
    </div>

    <!-- Right: actions + user -->
    <div class="flex items-center gap-4">
      <button
        class="p-2 text-on-surface-variant hover:bg-surface-container-high rounded-full transition-colors"
        title="Notifications"
      >
        <span class="material-symbols-outlined">notifications</span>
      </button>

      <div class="flex items-center gap-3 pl-4 border-l border-surface-variant/30">
        <div
          class="h-8 w-8 rounded-full bg-surface-container-high flex items-center justify-center overflow-hidden"
        >
          <span class="material-symbols-outlined text-on-surface-variant">person</span>
        </div>

        <button
          @click="handleLogout"
          class="p-2 text-on-surface-variant hover:text-error hover:bg-error-container/10 rounded-full transition-colors"
          title="Logout"
        >
          <span class="material-symbols-outlined">logout</span>
        </button>
      </div>
    </div>
  </header>
</template>
