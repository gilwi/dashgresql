<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/api'

const auth = useAuthStore()

// --- State ---
const databases = ref([])
const selectedDb = ref(null)
const schemas = ref([])
const selectedSchema = ref(null)
const selectedTable = ref(null)
const tableDetails = ref(null)

const isLoadingDbs = ref(false)
const isLoadingSchemas = ref(false)
const isLoadingTable = ref(false)
const error = ref('')

// --- Data fetching ---
onMounted(async () => {
  isLoadingDbs.value = true
  try {
    const res = await api.get('/api/databases/')
    databases.value = res.data
  } catch {
    error.value = 'Failed to load databases'
  } finally {
    isLoadingDbs.value = false
  }
})

const selectDatabase = async (db) => {
  selectedDb.value = db
  schemas.value = []
  selectedSchema.value = null
  selectedTable.value = null
  tableDetails.value = null
  error.value = ''

  isLoadingSchemas.value = true
  try {
    const res = await api.get(`/api/databases/${db.id}/schemas`)
    schemas.value = res.data
    if (schemas.value.length) selectSchema(schemas.value[0])
  } catch {
    error.value = 'Failed to load schemas'
  } finally {
    isLoadingSchemas.value = false
  }
}

const selectSchema = (schema) => {
  selectedSchema.value = schema
  selectedTable.value = null
  tableDetails.value = null
}

const selectTable = async (table) => {
  selectedTable.value = table
  tableDetails.value = null
  error.value = ''

  isLoadingTable.value = true
  try {
    const res = await api.get(
      `/api/databases/${selectedDb.value.id}/schemas/${selectedSchema.value.name}/tables/${table.name}`,
    )
    tableDetails.value = res.data
  } catch {
    error.value = 'Failed to load table details'
  } finally {
    isLoadingTable.value = false
  }
}

// --- Helpers ---
const getConstraintsForColumn = (columnName) => {
  if (!tableDetails.value) return []
  return tableDetails.value.constraints.filter((c) => c.column === columnName)
}

const getConstraintBadgeClass = (type) => {
  const classes = {
    'PRIMARY KEY': 'bg-primary/20 text-primary',
    'FOREIGN KEY': 'bg-secondary-container text-on-secondary-container',
    UNIQUE: 'bg-tertiary-container text-on-tertiary-container',
    CHECK: 'bg-surface-container-high text-on-surface-variant',
  }
  return classes[type] ?? 'bg-surface-container text-on-surface-variant'
}

const getConstraintIcon = (type) => {
  const icons = {
    'PRIMARY KEY': 'key',
    'FOREIGN KEY': 'link',
    UNIQUE: 'fingerprint',
    CHECK: 'rule',
  }
  return icons[type] ?? 'info'
}

const formatRowCount = (count) => {
  if (count >= 1_000_000) return `${(count / 1_000_000).toFixed(1)}M`
  if (count >= 1_000) return `${(count / 1_000).toFixed(1)}K`
  return count.toString()
}

const rightPanelView = computed(() => {
  if (selectedTable.value && tableDetails.value) return 'table-detail'
  if (selectedSchema.value) return 'schema-overview'
  return 'empty'
})
</script>

<template>
  <div class="flex flex-col h-full">
    <!-- Header -->
    <div class="mb-8">
      <nav
        class="flex gap-2 text-[0.65rem] font-bold text-on-surface-variant mb-2 uppercase tracking-[0.15em]"
      >
        <span>Production Cluster</span>
        <span class="text-outline-variant opacity-40">/</span>
        <span class="text-primary">Schemas</span>
      </nav>
      <div class="flex items-end justify-between">
        <h2 class="text-4xl font-black text-on-surface tracking-tighter">Database Blueprint</h2>

        <!-- Database picker -->
        <div class="flex items-center gap-3">
          <span class="text-[0.65rem] font-bold text-on-surface-variant uppercase tracking-widest">
            Database
          </span>
          <select
            @change="(e) => selectDatabase(databases.find((d) => d.id === e.target.value))"
            class="h-10 px-4 bg-surface-container-lowest rounded-xl outline-1 outline-outline-variant/20 focus:outline-primary text-sm font-bold text-on-surface"
            :disabled="isLoadingDbs"
          >
            <option value="" disabled :selected="!selectedDb">
              {{ isLoadingDbs ? 'Loading...' : 'Select a database' }}
            </option>
            <option v-for="db in databases" :key="db.id" :value="db.id">
              {{ db.name }}
            </option>
          </select>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-if="!selectedDb" class="flex-1 flex items-center justify-center">
      <div class="text-center space-y-3">
        <span class="material-symbols-outlined text-5xl text-on-surface-variant opacity-30"
          >schema</span
        >
        <p class="text-on-surface-variant font-medium">Select a database to explore its schemas</p>
      </div>
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="flex-1 flex items-center justify-center">
      <p class="text-red-400 text-sm font-medium">{{ error }}</p>
    </div>

    <!-- Loading schemas -->
    <div v-else-if="isLoadingSchemas" class="flex-1 flex items-center justify-center">
      <span class="material-symbols-outlined animate-spin text-primary text-3xl"
        >progress_activity</span
      >
    </div>

    <!-- Main content -->
    <div v-else class="flex-1 flex gap-8 min-h-0">
      <!-- Left sidebar: schemas + tables -->
      <div class="w-64 space-y-6 overflow-y-auto">
        <div v-for="schema in schemas" :key="schema.name">
          <button
            @click="selectSchema(schema)"
            class="w-full flex items-center justify-between px-4 py-3 rounded-xl transition-all mb-1"
            :class="
              selectedSchema?.name === schema.name
                ? 'bg-primary text-on-primary shadow-ambient'
                : 'hover:bg-surface-container-high text-on-surface'
            "
          >
            <div class="flex items-center gap-3">
              <span class="material-symbols-outlined text-sm">schema</span>
              <span class="text-sm font-bold">{{ schema.name }}</span>
            </div>
            <span class="text-[0.6rem] opacity-60 font-mono">{{ schema.tables.length }}T</span>
          </button>

          <!-- Tables under selected schema -->
          <div v-if="selectedSchema?.name === schema.name" class="ml-4 space-y-0.5">
            <button
              v-for="table in schema.tables"
              :key="table.name"
              @click="selectTable(table)"
              class="w-full flex items-center justify-between px-3 py-2 rounded-lg transition-all text-left"
              :class="
                selectedTable?.name === table.name
                  ? 'bg-primary/10 text-primary'
                  : 'hover:bg-surface-container-high text-on-surface-variant'
              "
            >
              <div class="flex items-center gap-2">
                <span class="material-symbols-outlined text-xs">table</span>
                <span class="text-xs font-bold">{{ table.name }}</span>
              </div>
              <span class="text-[0.55rem] font-mono opacity-50">
                {{ formatRowCount(table.row_count) }}
              </span>
            </button>
          </div>
        </div>
      </div>

      <!-- Right panel: table details -->
      <div
        class="flex-1 bg-surface-container-lowest rounded-3xl shadow-ambient p-8 overflow-y-auto"
      >
        <!-- Loading table -->
        <div v-if="isLoadingTable" class="h-full flex items-center justify-center">
          <span class="material-symbols-outlined animate-spin text-primary text-3xl"
            >progress_activity</span
          >
        </div>

        <!-- Schema overview -->
        <template v-else-if="rightPanelView === 'schema-overview'">
          <div class="flex justify-between items-start mb-8">
            <div>
              <h4 class="text-2xl font-black text-on-surface tracking-tight">
                {{ selectedSchema.name }}
              </h4>
              <p class="text-xs text-on-surface-variant font-medium uppercase tracking-wider mt-1">
                {{ selectedSchema.tables.length }} tables
              </p>
            </div>
          </div>

          <table class="w-full text-left">
            <thead class="border-b border-surface-variant/10">
              <tr>
                <th
                  class="py-4 text-[0.65rem] font-black text-on-surface-variant uppercase tracking-widest"
                >
                  Table
                </th>
                <th
                  class="py-4 text-[0.65rem] font-black text-on-surface-variant uppercase tracking-widest"
                >
                  Rows
                </th>
                <th
                  class="py-4 text-[0.65rem] font-black text-on-surface-variant uppercase tracking-widest"
                >
                  Size
                </th>
                <th class="py-4"></th>
              </tr>
            </thead>
            <tbody class="divide-y divide-surface-variant/5">
              <tr
                v-for="table in selectedSchema.tables"
                :key="table.name"
                class="group hover:bg-surface-container-low/30 transition-colors cursor-pointer"
                @click="selectTable(table)"
              >
                <td class="py-4">
                  <div class="flex items-center gap-3">
                    <div
                      class="w-8 h-8 rounded-lg bg-primary-container/40 text-primary flex items-center justify-center"
                    >
                      <span class="material-symbols-outlined text-sm">table</span>
                    </div>
                    <span class="text-sm font-bold text-on-surface">{{ table.name }}</span>
                  </div>
                </td>
                <td class="py-4 text-sm font-mono text-on-surface-variant">
                  <span
                    :title="
                      table.is_estimate
                        ? 'Estimated (table too large for exact count)'
                        : 'Exact count'
                    "
                    :class="table.is_estimate ? 'opacity-60' : ''"
                  >
                    {{ table.is_estimate ? '~' : '' }}{{ formatRowCount(table.row_count) }}
                  </span>
                </td>
                <td class="py-4 text-sm font-mono text-on-surface-variant">
                  {{ table.size }}
                </td>
                <td class="py-4 text-right">
                  <span
                    class="material-symbols-outlined text-on-surface-variant opacity-0 group-hover:opacity-100 transition-opacity text-sm"
                  >
                    arrow_forward
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </template>

        <!-- Table detail -->
        <template v-else-if="rightPanelView === 'table-detail'">
          <!-- Table header -->
          <div class="flex justify-between items-start mb-8">
            <div>
              <h4 class="text-2xl font-black text-on-surface tracking-tight">
                {{ selectedSchema.name }}.{{ selectedTable.name }}
              </h4>
              <div class="flex items-center gap-4 mt-1">
                <p class="text-xs text-on-surface-variant font-medium uppercase tracking-wider">
                  <span
                    :title="selectedTable.is_estimate ? 'Estimated row count' : 'Exact row count'"
                  >
                    {{ selectedTable.is_estimate ? '~' : ''
                    }}{{ formatRowCount(selectedTable.row_count) }} rows
                  </span>
                  · {{ selectedTable.size }}
                </p>
                <p class="text-xs text-on-surface-variant font-medium uppercase tracking-wider">
                  {{ selectedTable.size }}
                </p>
              </div>
            </div>
            <button
              @click="selectTable(selectedTable)"
              class="p-2 hover:bg-surface-container-high rounded-lg text-on-surface-variant transition-colors"
            >
              <span class="material-symbols-outlined">refresh</span>
            </button>
          </div>

          <!-- Columns table -->
          <h5
            class="text-[0.65rem] font-black text-on-surface-variant uppercase tracking-widest mb-4 opacity-60"
          >
            Columns
          </h5>
          <table class="w-full text-left mb-10">
            <thead class="border-b border-surface-variant/10">
              <tr>
                <th
                  class="py-4 text-[0.65rem] font-black text-on-surface-variant uppercase tracking-widest"
                >
                  Column
                </th>
                <th
                  class="py-4 text-[0.65rem] font-black text-on-surface-variant uppercase tracking-widest"
                >
                  Type
                </th>
                <th
                  class="py-4 text-[0.65rem] font-black text-on-surface-variant uppercase tracking-widest"
                >
                  Nullable
                </th>
                <th
                  class="py-4 text-[0.65rem] font-black text-on-surface-variant uppercase tracking-widest"
                >
                  Default
                </th>
                <th
                  class="py-4 text-[0.65rem] font-black text-on-surface-variant uppercase tracking-widest"
                >
                  Constraints
                </th>
              </tr>
            </thead>
            <tbody class="divide-y divide-surface-variant/5">
              <tr
                v-for="col in tableDetails.columns"
                :key="col.name"
                class="group hover:bg-surface-container-low/30 transition-colors"
              >
                <td class="py-4">
                  <div class="flex items-center gap-2">
                    <span
                      v-if="getConstraintsForColumn(col.name).some((c) => c.type === 'PRIMARY KEY')"
                      class="material-symbols-outlined text-sm text-primary"
                      >key</span
                    >
                    <span
                      v-else-if="
                        getConstraintsForColumn(col.name).some((c) => c.type === 'FOREIGN KEY')
                      "
                      class="material-symbols-outlined text-sm text-secondary"
                      >link</span
                    >
                    <span
                      v-else
                      class="material-symbols-outlined text-sm text-on-surface-variant opacity-30"
                    >
                      radio_button_unchecked
                    </span>
                    <span class="text-sm font-bold text-on-surface">{{ col.name }}</span>
                  </div>
                </td>
                <td
                  class="py-4 font-mono text-xs text-on-surface-variant uppercase tracking-tighter"
                >
                  {{ col.type }}
                </td>
                <td class="py-4">
                  <span
                    :class="col.nullable ? 'text-on-surface-variant opacity-40' : 'text-primary'"
                    class="text-xs font-bold uppercase"
                  >
                    {{ col.nullable ? 'yes' : 'no' }}
                  </span>
                </td>
                <td class="py-4 text-xs text-on-surface-variant font-mono italic">
                  {{ col.default ?? '—' }}
                </td>
                <td class="py-4">
                  <div class="flex flex-wrap gap-1">
                    <span
                      v-for="constraint in getConstraintsForColumn(col.name)"
                      :key="constraint.name"
                      :class="getConstraintBadgeClass(constraint.type)"
                      class="px-2 py-0.5 rounded text-[0.6rem] font-black uppercase tracking-tighter flex items-center gap-1"
                      :title="
                        constraint.type === 'FOREIGN KEY'
                          ? `→ ${constraint.foreign_table}.${constraint.foreign_column}`
                          : constraint.name
                      "
                    >
                      <span class="material-symbols-outlined text-[0.7rem]">
                        {{ getConstraintIcon(constraint.type) }}
                      </span>
                      {{
                        constraint.type === 'FOREIGN KEY'
                          ? `→ ${constraint.foreign_table}`
                          : constraint.type
                      }}
                    </span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>

          <!-- Indexes -->
          <h5
            class="text-[0.65rem] font-black text-on-surface-variant uppercase tracking-widest mb-4 opacity-60"
          >
            Indexes
          </h5>
          <div class="space-y-2">
            <div
              v-for="index in tableDetails.indexes"
              :key="index.name"
              class="px-5 py-4 bg-surface-container-low rounded-xl"
            >
              <div class="flex items-center gap-2 mb-1">
                <span class="material-symbols-outlined text-sm text-on-surface-variant">lan</span>
                <span class="text-sm font-bold text-on-surface">{{ index.name }}</span>
              </div>
              <p class="font-mono text-[0.65rem] text-on-surface-variant opacity-60 ml-6">
                {{ index.definition }}
              </p>
            </div>
            <p
              v-if="!tableDetails.indexes.length"
              class="text-xs text-on-surface-variant italic opacity-50"
            >
              No indexes defined on this table.
            </p>
          </div>
        </template>

        <!-- Nothing selected -->
        <div v-else class="h-full flex items-center justify-center">
          <div class="text-center space-y-3">
            <span class="material-symbols-outlined text-4xl text-on-surface-variant opacity-30"
              >table</span
            >
            <p class="text-on-surface-variant text-sm font-medium">
              Select a table to inspect its structure
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
