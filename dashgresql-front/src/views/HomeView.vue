<script setup>
import { ref } from 'vue'

const databases = ref([
  {
    id: 'db-0192-8491',
    name: 'production_db',
    status: 'Active',
    connections: 84,
    maxConnections: 150,
    size: '412.5 GB',
    lastBackup: '2 hours ago',
    type: 'terminal',
  },
  {
    id: 'db-0294-1182',
    name: 'analytics_master',
    status: 'Idle',
    connections: 12,
    maxConnections: 500,
    size: '892.1 GB',
    lastBackup: '6 hours ago',
    type: 'storage',
  },
  {
    id: 'db-8821-4402',
    name: 'staging_db',
    status: 'Active',
    connections: 46,
    maxConnections: 100,
    size: '45.0 GB',
    lastBackup: 'Just now',
    type: 'science',
  },
])

// Helper for status colors
const getStatusClass = (status) => {
  if (status === 'Active') return 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.4)]'
  return 'bg-blue-400'
}
</script>

<template>
  <div class="bg-surface-container-low rounded-2xl overflow-hidden shadow-ambient">
    <div class="overflow-x-auto">
      <table class="w-full text-left border-collapse">
        <thead class="bg-surface-container-low border-b border-surface-variant/20">
          <tr>
            <th
              class="px-8 py-4 text-[0.7rem] font-bold uppercase tracking-wider text-on-surface-variant"
            >
              Database Name
            </th>
            <th
              class="px-6 py-4 text-[0.7rem] font-bold uppercase tracking-wider text-on-surface-variant"
            >
              Status
            </th>
            <th
              class="px-6 py-4 text-[0.7rem] font-bold uppercase tracking-wider text-on-surface-variant"
            >
              Connections
            </th>
            <th
              class="px-6 py-4 text-[0.7rem] font-bold uppercase tracking-wider text-on-surface-variant"
            >
              Size
            </th>
            <th
              class="px-6 py-4 text-[0.7rem] font-bold uppercase tracking-wider text-on-surface-variant"
            >
              Last Backup
            </th>
            <th class="px-8 py-4"></th>
          </tr>
        </thead>
        <tbody class="bg-surface-container-lowest">
          <tr
            v-for="db in databases"
            :key="db.id"
            class="hover:bg-surface-container-high transition-colors group border-t border-surface-variant/10 first:border-t-0"
          >
            <td class="px-8 py-5">
              <div class="flex items-center gap-3">
                <div
                  class="w-8 h-8 rounded bg-primary-container text-primary flex items-center justify-center"
                >
                  <span class="material-symbols-outlined text-lg">{{ db.type }}</span>
                </div>
                <div>
                  <div class="font-bold text-on-surface">{{ db.name }}</div>
                  <div class="text-[0.65rem] text-on-surface-variant font-mono uppercase">
                    UUID: {{ db.id }}
                  </div>
                </div>
              </div>
            </td>
            <td class="px-6 py-5">
              <div class="flex items-center gap-2">
                <span class="w-2 h-2 rounded-full" :class="getStatusClass(db.status)"></span>
                <span class="text-sm font-semibold text-on-surface">{{ db.status }}</span>
              </div>
            </td>
            <td class="px-6 py-5">
              <div class="text-sm font-medium text-on-surface">
                {{ db.connections }} <span class="text-on-surface-variant text-xs">clients</span>
              </div>
              <div class="w-24 h-1 bg-surface-container rounded-full mt-1.5 overflow-hidden">
                <div
                  class="h-full bg-primary transition-all duration-500"
                  :style="{ width: (db.connections / db.maxConnections) * 100 + '%' }"
                ></div>
              </div>
            </td>
            <td class="px-6 py-5 font-medium text-on-surface">{{ db.size }}</td>
            <td class="px-6 py-5 text-sm text-on-surface-variant">{{ db.lastBackup }}</td>
            <td class="px-8 py-5 text-right">
              <button
                class="opacity-0 group-hover:opacity-100 transition-opacity p-2 hover:bg-surface-container-highest rounded-md"
              >
                <span class="material-symbols-outlined text-on-surface-variant">more_vert</span>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
