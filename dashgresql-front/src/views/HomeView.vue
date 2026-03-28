<script setup>
import { ref, computed } from 'vue'
import BaseModal from '../components/BaseModal.vue'

// --- State Management ---
const isModalOpen = ref(false)
const newDb = ref({ name: '', type: 'terminal' })

// Mock Data Store
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

// --- Logic ---
const handleAddDatabase = () => {
  if (!newDb.value.name) return

  databases.value.push({
    id: `db-${Math.floor(Math.random() * 9000) + 1000}`,
    name: newDb.value.name,
    status: 'Active',
    connections: 0,
    maxConnections: 100,
    size: '0 GB',
    lastBackup: 'Just now',
    type: newDb.value.type,
  })

  // Reset UI
  newDb.value = { name: '', type: 'terminal' }
  isModalOpen.value = false

  // Mock Traffic Data (Heights in percentage)
}

const trafficBars = ref([40, 60, 35, 80, 45, 70, 55, 90, 30, 50, 40, 25, 100, 75, 50, 85, 30])

const getStatusColor = (status) => {
  return status === 'Active' ? 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.4)]' : 'bg-blue-400'
}
</script>

<template>
  <div class="flex justify-between items-end mb-10">
    <div>
      <nav
        class="flex gap-2 text-[0.65rem] font-bold text-on-surface-variant mb-2 uppercase tracking-[0.15em]"
      >
        <span>Server</span>
        <span class="text-outline-variant opacity-40">/</span>
        <span class="text-primary">Production Cluster</span>
      </nav>
      <h2 class="text-4xl font-black text-on-surface tracking-tighter">Databases</h2>
    </div>

    <button
      @click="isModalOpen = true"
      class="bg-primary hover:bg-primary-dim text-on-primary px-6 py-2.5 rounded-md font-bold text-sm shadow-ambient flex items-center gap-2 transition-all active:scale-95"
    >
      <span class="material-symbols-outlined text-sm">add</span>
      <span>Add Database</span>
    </button>
  </div>

  <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-10">
    <div
      class="bg-surface-container-lowest p-6 rounded-2xl shadow-ambient hover:-translate-y-1 transition-all duration-300 group"
    >
      <p
        class="text-[0.65rem] text-on-surface-variant font-bold tracking-[0.1em] mb-3 uppercase opacity-70"
      >
        Total Storage
      </p>
      <div class="flex items-end gap-2">
        <span class="text-3xl font-black text-on-surface tracking-tighter">1.4</span>
        <span class="text-sm font-bold text-on-surface-variant mb-1">TB</span>
      </div>
      <div class="mt-5 h-1.5 w-full bg-surface-container rounded-full overflow-hidden">
        <div class="h-full bg-primary w-[65%] group-hover:bg-primary-dim transition-colors"></div>
      </div>
    </div>

    <div
      class="bg-surface-container-lowest p-6 rounded-2xl shadow-ambient hover:-translate-y-1 transition-all"
    >
      <p
        class="text-[0.65rem] text-on-surface-variant font-bold tracking-[0.1em] mb-3 uppercase opacity-70"
      >
        Active Connections
      </p>
      <div class="flex items-end gap-2">
        <span class="text-3xl font-black text-on-surface tracking-tighter">142</span>
        <span class="text-xs font-bold text-on-surface-variant mb-1">/ 500</span>
      </div>
      <div class="mt-5 flex gap-1.5">
        <span class="h-1.5 flex-1 bg-primary rounded-full"></span>
        <span class="h-1.5 flex-1 bg-primary rounded-full"></span>
        <span v-for="i in 3" :key="i" class="h-1.5 flex-1 bg-primary/20 rounded-full"></span>
      </div>
    </div>

    <div
      class="bg-surface-container-lowest p-6 rounded-2xl shadow-ambient hover:-translate-y-1 transition-all"
    >
      <p
        class="text-[0.65rem] text-on-surface-variant font-bold tracking-[0.1em] mb-3 uppercase opacity-70"
      >
        Avg Latency
      </p>
      <div class="flex items-end gap-2">
        <span class="text-3xl font-black text-on-surface tracking-tighter">12</span>
        <span class="text-sm font-bold text-on-surface-variant mb-1">ms</span>
      </div>
      <p class="mt-3 text-[0.7rem] text-green-600 font-bold flex items-center gap-1">
        <span class="material-symbols-outlined text-[1rem]">trending_down</span>
        4% FROM LAST HOUR
      </p>
    </div>

    <div
      class="bg-surface-container-lowest p-6 rounded-2xl shadow-ambient hover:-translate-y-1 transition-all"
    >
      <p
        class="text-[0.65rem] text-on-surface-variant font-bold tracking-[0.1em] mb-3 uppercase opacity-70"
      >
        Uptime
      </p>
      <div class="flex items-end gap-2">
        <span class="text-3xl font-black text-on-surface tracking-tighter">99.99</span>
        <span class="text-sm font-bold text-on-surface-variant mb-1">%</span>
      </div>
      <p class="mt-3 text-[0.7rem] text-on-surface-variant font-medium">Last 30 days</p>
    </div>
  </div>

  <div class="bg-surface-container-low rounded-3xl overflow-hidden shadow-ambient">
    <div class="px-8 py-5 flex items-center justify-between border-b border-surface-variant/10">
      <div class="flex gap-2">
        <button
          class="px-5 py-2 bg-secondary-container text-on-secondary-container rounded-full text-[0.65rem] font-black uppercase tracking-wider shadow-sm"
        >
          All Instances
        </button>
        <button
          class="px-5 py-2 text-on-surface-variant hover:bg-surface-container-high rounded-full text-[0.65rem] font-bold uppercase tracking-wider transition-colors"
        >
          Production
        </button>
        <button
          class="px-5 py-2 text-on-surface-variant hover:bg-surface-container-high rounded-full text-[0.65rem] font-bold uppercase tracking-wider transition-colors"
        >
          Development
        </button>
      </div>
      <div
        class="flex items-center gap-2 text-on-surface-variant text-[0.65rem] font-bold uppercase tracking-widest"
      >
        <span>Sort by:</span>
        <button
          class="flex items-center gap-1 text-on-surface font-black hover:text-primary transition-colors"
        >
          Size <span class="material-symbols-outlined text-[1rem]">expand_more</span>
        </button>
      </div>
    </div>

    <div class="overflow-x-auto bg-surface-container-lowest">
      <table class="w-full text-left border-collapse">
        <thead class="bg-surface-container-low/50 border-b border-surface-variant/10">
          <tr>
            <th
              class="px-10 py-5 text-[0.7rem] font-bold uppercase tracking-widest text-on-surface-variant/60"
            >
              Database Name
            </th>
            <th
              class="px-6 py-5 text-[0.7rem] font-bold uppercase tracking-widest text-on-surface-variant/60"
            >
              Status
            </th>
            <th
              class="px-6 py-5 text-[0.7rem] font-bold uppercase tracking-widest text-on-surface-variant/60"
            >
              Connections
            </th>
            <th
              class="px-6 py-5 text-[0.7rem] font-bold uppercase tracking-widest text-on-surface-variant/60"
            >
              Size
            </th>
            <th
              class="px-6 py-5 text-[0.7rem] font-bold uppercase tracking-widest text-on-surface-variant/60"
            >
              Last Backup
            </th>
            <th class="px-10 py-5"></th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="db in databases"
            :key="db.id"
            class="hover:bg-surface-container-high/40 transition-all group border-b border-surface-variant/5 last:border-0"
          >
            <td class="px-10 py-6">
              <div class="flex items-center gap-4">
                <div
                  class="w-10 h-10 rounded-xl bg-primary-container/40 text-primary flex items-center justify-center"
                >
                  <span class="material-symbols-outlined text-xl">{{ db.type }}</span>
                </div>
                <div>
                  <div class="font-bold text-on-surface text-base">{{ db.name }}</div>
                  <div
                    class="text-[0.6rem] text-on-surface-variant font-mono uppercase tracking-tighter"
                  >
                    ID: {{ db.id }}
                  </div>
                </div>
              </div>
            </td>
            <td class="px-6 py-6">
              <div class="flex items-center gap-2.5">
                <span
                  class="w-2.5 h-2.5 rounded-full transition-transform group-hover:scale-125"
                  :class="getStatusColor(db.status)"
                ></span>
                <span class="text-sm font-bold text-on-surface">{{ db.status }}</span>
              </div>
            </td>
            <td class="px-6 py-6">
              <div class="text-sm font-bold text-on-surface">
                {{ db.connections }} <span class="opacity-40 font-medium">clients</span>
              </div>
              <div class="w-24 h-1 bg-surface-container rounded-full mt-2 overflow-hidden">
                <div
                  class="h-full bg-primary rounded-full"
                  :style="{ width: (db.connections / db.maxConnections) * 100 + '%' }"
                ></div>
              </div>
            </td>
            <td class="px-6 py-6 font-bold text-sm text-on-surface">{{ db.size }}</td>
            <td class="px-6 py-6 text-sm text-on-surface-variant font-medium">
              {{ db.lastBackup }}
            </td>
            <td class="px-10 py-6 text-right">
              <button
                class="opacity-0 group-hover:opacity-100 transition-opacity p-2 hover:bg-surface-container-highest rounded-lg"
              >
                <span class="material-symbols-outlined text-on-surface-variant">more_vert</span>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
  <div class="mt-12">
    <h3
      class="text-[0.65rem] text-on-surface-variant font-black tracking-[0.2em] uppercase mb-6 opacity-60"
    >
      Infrastructure Traffic Distribution (Real-time)
    </h3>

    <div
      class="h-48 w-full bg-surface-container-low rounded-3xl p-8 relative overflow-hidden flex items-end gap-2 border-ghost"
    >
      <div
        v-for="(height, index) in trafficBars"
        :key="index"
        class="flex-1 bg-primary/20 rounded-t-lg transition-all duration-700 ease-in-out hover:bg-primary"
        :style="{ height: height + '%' }"
      ></div>

      <div
        class="absolute inset-0 flex items-center justify-center backdrop-blur-[2px] bg-surface-container-lowest/5"
      >
        <div
          class="bg-surface-container-lowest/80 backdrop-blur-md px-6 py-3 rounded-2xl shadow-ambient border border-white/20 flex items-center gap-3"
        >
          <span class="material-symbols-outlined text-primary animate-pulse">monitoring</span>
          <p class="text-[0.7rem] font-black text-on-surface uppercase tracking-widest">
            Live Monitoring Active
          </p>
        </div>
      </div>
    </div>
  </div>

  <BaseModal :show="isModalOpen" title="Register New Database" @close="isModalOpen = false">
    <form @submit.prevent="handleAddDatabase" class="space-y-6">
      <div class="space-y-2">
        <label class="text-[0.65rem] font-bold text-on-surface-variant uppercase tracking-widest"
          >Database Identity</label
        >
        <input
          v-model="newDb.name"
          type="text"
          placeholder="e.g. customer_analytics_v2"
          class="w-full h-12 px-4 bg-surface-container-lowest rounded-xl outline-1 outline-outline-variant/20 focus:outline-primary focus:ring-8 focus:ring-primary/5 transition-all placeholder:text-surface-dim"
          required
        />
      </div>

      <div class="space-y-2">
        <label class="text-[0.65rem] font-bold text-on-surface-variant uppercase tracking-widest"
          >Architecture Type</label
        >
        <select
          v-model="newDb.type"
          class="w-full h-12 px-4 bg-surface-container-lowest rounded-xl outline-1 outline-outline-variant/20 focus:outline-primary outline-none"
        >
          <option value="terminal">Standard Instance</option>
          <option value="storage">Data Warehouse</option>
          <option value="science">Experimental/Staging</option>
        </select>
      </div>

      <div class="pt-4">
        <button
          type="submit"
          class="w-full h-12 btn-primary-gradient text-on-primary font-bold rounded-xl shadow-ambient transition-transform active:scale-95"
        >
          Provision Resource
        </button>
      </div>
    </form>
  </BaseModal>
</template>
