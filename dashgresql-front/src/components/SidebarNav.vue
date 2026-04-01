<script setup>
// Nav items that are fully implemented and routed
const primaryLinks = [
  { to: '/', icon: 'database', label: 'Databases' },
  { to: '/schemas', icon: 'schema', label: 'Schemas' },
]

// Nav items that exist in the UI but aren't routed yet
const comingSoonLinks = [
  { icon: 'terminal', label: 'Query Console' },
  { icon: 'sync_alt', label: 'Replication' },
  { icon: 'list_alt', label: 'Logs' },
]
</script>

<template>
  <nav class="flex-1 space-y-1 px-4">
    <RouterLink
      v-for="link in primaryLinks"
      :key="link.to"
      :to="link.to"
      class="flex items-center gap-3 px-3 py-2.5 rounded-md transition-all duration-200"
      :class="
        $route.path === link.to
          ? 'text-primary font-bold bg-surface-container-lowest shadow-sm'
          : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high'
      "
    >
      <span class="material-symbols-outlined text-[1.25rem]">{{ link.icon }}</span>
      <span class="text-sm font-medium">{{ link.label }}</span>
    </RouterLink>

    <button
      v-for="link in comingSoonLinks"
      :key="link.label"
      disabled
      class="w-full flex items-center gap-3 px-3 py-2.5 text-on-surface-variant rounded-md transition-all duration-200 group opacity-50 cursor-not-allowed"
      :title="`${link.label} — coming soon`"
    >
      <span class="material-symbols-outlined text-[1.25rem]">{{ link.icon }}</span>
      <span class="text-sm font-medium">{{ link.label }}</span>
    </button>
  </nav>
</template>
