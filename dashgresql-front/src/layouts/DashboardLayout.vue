<script setup>
import { RouterView } from 'vue-router'
// import AppSidebar from '@/components/AppSidebar.vue'
// import AppTopbar from '@/components/AppTopbar.vue'
import AppSidebar from '../components/AppSidebar.vue'
import AppTopbar from '../components/AppTopbar.vue'
</script>

<template>
  <div
    class="min-h-screen bg-surface font-body text-on-surface selection:bg-primary-container selection:text-on-primary-container"
  >
    <AppSidebar />

    <main class="ml-64 min-h-screen flex flex-col">
      <AppTopbar />

      <div class="p-8 flex-1">
        <RouterView />
      </div>
    </main>
  </div>
</template>
