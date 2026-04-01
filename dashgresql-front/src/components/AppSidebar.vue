<script setup>
import SidebarBrand from './SidebarBrand.vue'
import SidebarNav from './SidebarNav.vue'
</script>

<template>
  <aside
    class="h-screen w-64 fixed left-0 top-0 z-50 bg-surface-container-low flex flex-col p-4 gap-y-2"
  >
    <SidebarBrand />
    <SidebarNav />

    <!-- Footer -->
    <div class="mt-auto pt-4 border-t border-surface-variant/20 px-4 pb-6 space-y-1">
      <a
        href="#"
        class="flex items-center gap-3 px-3 py-2 text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high rounded-md transition-all text-xs font-bold uppercase tracking-wider"
      >
        <span class="material-symbols-outlined text-[1rem]">help</span>
        <span>Docs</span>
      </a>
    </div>
  </aside>
</template>
