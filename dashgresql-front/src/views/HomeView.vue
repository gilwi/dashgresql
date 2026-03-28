<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import BaseModal from '../components/BaseModal.vue'
import api from '@/api'

const isModalOpen = ref(false)
const newDb = ref({
  name: '',
  host: '',
  port: 5432,
  db_user: '',
  password: '',
  pg_version: '16',
  max_connections: 100,
})
const databases = ref([])
const isSubmitting = ref(false)
const formError = ref('')

const trafficBars = ref([40, 60, 35, 80, 45, 70, 55, 90, 30, 50, 40, 25, 100, 75, 50, 85, 30])

const isChecking = ref(false)

const POLL_INTERVAL_MS = 60_000
let pollTimer = null

onMounted(async () => {
  const res = await api.get('/api/databases/')
  databases.value = res.data
  await checkAllConnections()

  // Start polling
  pollTimer = setInterval(checkAllConnections, POLL_INTERVAL_MS)
})

// Clean up on leave so the interval doesn't keep running in the background
onUnmounted(() => {
  clearInterval(pollTimer)
})

// Check all connections at once
const checkAllConnections = async () => {
  isChecking.value = true
  try {
    const res = await api.get('/api/databases/check-all')
    const results = res.data

    // Merge status + connection_count into each database
    databases.value = databases.value.map((db) => ({
      ...db,
      status: results[db.id]?.status ?? 'Unknown',
      connection_count: results[db.id]?.connection_count ?? 0,
      size: results[db.id]?.size ?? db.size, // fall back to stored value
      error: results[db.id]?.error ?? null,
    }))
  } catch (err) {
    console.error('Failed to check connections:', err)
  } finally {
    isChecking.value = false
  }
}

// Check a single database (for the per-row refresh button)
const checkConnection = async (dbId) => {
  const target = databases.value.find((d) => d.id === dbId)
  if (target) target.checking = true

  try {
    const res = await api.get(`/api/databases/${dbId}/check`)
    databases.value = databases.value.map((d) =>
      d.id === dbId
        ? {
            ...d,
            status: res.data.status,
            connection_count: res.data.connection_count,
            size: res.data.size ?? d.size, // fall back to stored value
            error: res.data.error,
            checking: false,
          }
        : d,
    )
  } catch (err) {
    console.error('Check failed:', err)
    if (target) target.checking = false
  }
}

const handleAddDatabase = async () => {
  if (!newDb.value.name) return
  formError.value = ''
  isSubmitting.value = true

  try {
    const res = await api.post('/api/databases/', {
      name: newDb.value.name,
      pg_version: newDb.value.pg_version,
      max_connections: newDb.value.max_connections,
      host: newDb.value.host,
      db_user: newDb.value.db_user,
      password: newDb.value.password,
    })

    databases.value.push(res.data)
    newDb.value = { name: '', pg_version: '16', max_connections: 100 }
    isModalOpen.value = false
  } catch (err) {
    formError.value = err.response?.data?.error ?? 'Failed to create database'
  } finally {
    isSubmitting.value = false
  }
}

const getStatusColor = (status) => {
  const colors = {
    Active: 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.4)]',
    Idle: 'bg-blue-400',
    Unreachable: 'bg-red-500',
    Error: 'bg-yellow-500',
    Unknown: 'bg-surface-dim',
  }
  return colors[status] ?? 'bg-surface-dim'
}

const totalStorage = computed(() => {
  const toBytes = (sizeStr) => {
    if (!sizeStr) return 0
    const units = { bytes: 1, kb: 1024, mb: 1024 ** 2, gb: 1024 ** 3, tb: 1024 ** 4 }
    const match = sizeStr.toLowerCase().match(/^([\d.]+)\s*(\w+)$/)
    if (!match) return 0
    const value = parseFloat(match[1])
    const unit = match[2].replace(/s$/, '') // normalize 'bytes' → 'byte', etc.
    return value * (units[unit] ?? 1)
  }

  const toHuman = (bytes) => {
    if (bytes >= 1024 ** 4) return `${(bytes / 1024 ** 4).toFixed(1)} TB`
    if (bytes >= 1024 ** 3) return `${(bytes / 1024 ** 3).toFixed(1)} GB`
    if (bytes >= 1024 ** 2) return `${(bytes / 1024 ** 2).toFixed(1)} MB`
    if (bytes >= 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${bytes} bytes`
  }

  const totalBytes = databases.value.reduce((sum, db) => sum + toBytes(db.size), 0)
  return toHuman(totalBytes)
})

// Split into value and unit for display (e.g. "1.4" and "TB")
const totalStorageValue = computed(() => totalStorage.value.split(' ')[0])
const totalStorageUnit = computed(() => totalStorage.value.split(' ')[1])

const totalConnections = computed(() =>
  databases.value.reduce((sum, db) => sum + (db.connection_count ?? 0), 0),
)

const totalMaxConnections = computed(() =>
  databases.value.reduce((sum, db) => sum + (db.max_connections ?? 0), 0),
)

const connectionRatio = computed(() =>
  totalMaxConnections.value > 0
    ? Math.min(totalConnections.value / totalMaxConnections.value, 1)
    : 0,
)
</script>

<template>
  <div class="flex justify-between items-end mb-10">
    <div>
      <nav
        class="flex gap-2 text-[0.65rem] font-bold text-on-surface-variant mb-2 uppercase tracking-[0.15em]"
      >
        <span></span>
        <span class="text-outline-variant opacity-40">/</span>
        <span class="text-primary">databases</span>
      </nav>
      <!-- <h2 class="text-4xl font-black text-on-surface tracking-tighter">Databases</h2> -->
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
        <span class="text-3xl font-black text-on-surface tracking-tighter">
          {{ totalStorageValue }}
        </span>
        <span class="text-sm font-bold text-on-surface-variant mb-1">
          {{ totalStorageUnit }}
        </span>
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
        <span class="text-3xl font-black text-on-surface tracking-tighter">
          {{ totalConnections }}
        </span>
        <span class="text-xs font-bold text-on-surface-variant mb-1">
          / {{ totalMaxConnections }}
        </span>
      </div>

      <div class="mt-5 flex gap-1.5">
        <div class="w-full h-1.5 bg-primary/20 rounded-full overflow-hidden">
          <div
            class="h-full bg-primary rounded-full transition-all duration-500"
            :style="{ width: connectionRatio * 100 + '%' }"
          ></div>
        </div>
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
      <div class="flex items-center gap-3">
        <span class="text-on-surface-variant text-[0.65rem] font-bold uppercase tracking-widest">
          {{ isChecking ? 'Checking...' : 'Last checked just now' }}
        </span>
        <button
          @click="checkAllConnections"
          :disabled="isChecking"
          class="flex items-center gap-1.5 px-4 py-2 bg-surface-container-high hover:bg-surface-container-highest rounded-full text-[0.65rem] font-black uppercase tracking-wider transition-all disabled:opacity-50"
        >
          <span class="material-symbols-outlined text-sm" :class="{ 'animate-spin': isChecking }">
            refresh
          </span>
          Refresh
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
                  <span class="material-symbols-outlined text-xl">database</span>
                  <!-- <span class="material-symbols-outlined text-xl">{{ db.type }}</span> -->
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
                <div>
                  <span class="text-sm font-bold text-on-surface">{{ db.status }}</span>
                  <p
                    v-if="db.error"
                    class="text-[0.6rem] text-red-400 font-mono mt-0.5 max-w-[160px] truncate"
                    :title="db.error"
                  >
                    {{ db.error }}
                  </p>
                </div>
              </div>
            </td>
            <td class="px-6 py-6">
              <div class="text-sm font-bold text-on-surface">
                {{ db.connection_count }}
                <span class="opacity-40 font-medium">clients</span>
              </div>
              <div class="w-24 h-1 bg-surface-container rounded-full mt-2 overflow-hidden">
                <div
                  class="h-full bg-primary rounded-full transition-all duration-500"
                  :style="{
                    width: Math.min((db.connection_count / db.max_connections) * 100, 100) + '%',
                  }"
                ></div>
              </div>
            </td>
            <td class="px-6 py-6 font-bold text-sm text-on-surface">{{ db.size }}</td>
            <td class="px-6 py-6 text-sm text-on-surface-variant font-medium">
              {{ db.lastBackup }}
            </td>
            <td class="px-10 py-6 text-right">
              <div
                class="flex items-center justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity"
              >
                <button
                  @click="checkConnection(db.id)"
                  :disabled="db.checking"
                  class="p-2 hover:bg-surface-container-highest rounded-lg"
                  title="Check connection"
                >
                  <span
                    class="material-symbols-outlined text-on-surface-variant text-sm"
                    :class="{ 'animate-spin': db.checking }"
                  >
                    refresh
                  </span>
                </button>
                <button class="p-2 hover:bg-surface-container-highest rounded-lg">
                  <span class="material-symbols-outlined text-on-surface-variant">more_vert</span>
                </button>
              </div>
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
          >Database Name</label
        >
        <input
          v-model="newDb.name"
          type="text"
          placeholder="e.g. customer_analytics_v2"
          class="w-full h-12 px-4 bg-surface-container-lowest rounded-xl outline-1 outline-outline-variant/20 focus:outline-primary focus:ring-8 focus:ring-primary/5 transition-all placeholder:text-surface-dim"
          required
        />
      </div>

      <!-- Host + Port side by side -->
      <div class="flex gap-3">
        <div class="space-y-2 flex-1">
          <label class="text-[0.65rem] font-bold text-on-surface-variant uppercase tracking-widest"
            >Host</label
          >
          <input
            v-model="newDb.host"
            type="text"
            placeholder="e.g. db.example.com"
            class="w-full h-12 px-4 bg-surface-container-lowest rounded-xl outline-1 outline-outline-variant/20 focus:outline-primary focus:ring-8 focus:ring-primary/5 transition-all placeholder:text-surface-dim"
            required
          />
        </div>
        <div class="space-y-2 w-28">
          <label class="text-[0.65rem] font-bold text-on-surface-variant uppercase tracking-widest"
            >Port</label
          >
          <input
            v-model.number="newDb.port"
            type="number"
            placeholder="5432"
            class="w-full h-12 px-4 bg-surface-container-lowest rounded-xl outline-1 outline-outline-variant/20 focus:outline-primary focus:ring-8 focus:ring-primary/5 transition-all placeholder:text-surface-dim"
            required
          />
        </div>
      </div>

      <div class="space-y-2">
        <label class="text-[0.65rem] font-bold text-on-surface-variant uppercase tracking-widest"
          >DB User</label
        >
        <input
          v-model="newDb.db_user"
          type="text"
          placeholder="e.g. postgres"
          class="w-full h-12 px-4 bg-surface-container-lowest rounded-xl outline-1 outline-outline-variant/20 focus:outline-primary focus:ring-8 focus:ring-primary/5 transition-all placeholder:text-surface-dim"
          required
        />
      </div>

      <div class="space-y-2">
        <label class="text-[0.65rem] font-bold text-on-surface-variant uppercase tracking-widest"
          >Password</label
        >
        <input
          v-model="newDb.password"
          type="password"
          placeholder="••••••••"
          class="w-full h-12 px-4 bg-surface-container-lowest rounded-xl outline-1 outline-outline-variant/20 focus:outline-primary focus:ring-8 focus:ring-primary/5 transition-all placeholder:text-surface-dim"
          required
        />
      </div>

      <div class="space-y-2">
        <label class="text-[0.65rem] font-bold text-on-surface-variant uppercase tracking-widest"
          >PostgreSQL Version</label
        >
        <select
          v-model="newDb.pg_version"
          class="w-full h-12 px-4 bg-surface-container-lowest rounded-xl outline-1 outline-outline-variant/20 focus:outline-primary outline-none"
        >
          <option value="14">PostgreSQL 14</option>
          <option value="15">PostgreSQL 15</option>
          <option value="16">PostgreSQL 16</option>
          <option value="17">PostgreSQL 17</option>
        </select>
      </div>

      <div class="space-y-2">
        <label class="text-[0.65rem] font-bold text-on-surface-variant uppercase tracking-widest"
          >Max Connections</label
        >
        <input
          v-model.number="newDb.max_connections"
          type="number"
          min="10"
          max="10000"
          placeholder="100"
          class="w-full h-12 px-4 bg-surface-container-lowest rounded-xl outline-1 outline-outline-variant/20 focus:outline-primary focus:ring-8 focus:ring-primary/5 transition-all placeholder:text-surface-dim"
          required
        />
      </div>

      <p v-if="formError" class="text-sm text-red-400 text-center">{{ formError }}</p>

      <div class="pt-4">
        <button
          type="submit"
          :disabled="isSubmitting"
          class="w-full h-12 bg-primary text-on-primary font-bold rounded-xl shadow-ambient transition-transform active:scale-95 disabled:opacity-50"
        >
          {{ isSubmitting ? 'Provisioning...' : 'Provision Resource' }}
        </button>
      </div>
    </form>
  </BaseModal>
</template>
