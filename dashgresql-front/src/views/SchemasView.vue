<script setup>
import { ref } from 'vue'

const schemas = ref([
  { name: 'public', tables: ['users', 'orders', 'products'], functions: 12 },
  { name: 'auth', tables: ['sessions', 'accounts'], functions: 4 },
  { name: 'inventory', tables: ['warehouses', 'stock_levels', 'suppliers'], functions: 8 },
])

const selectedSchema = ref(schemas.value[0])
const selectedTable = ref('users')

const selectSchema = (schema) => {
  selectedSchema.value = schema
  selectedTable.value = schema.tables[0]
}
</script>

<template>
  <div class="flex flex-col h-full">
    <div class="mb-8">
      <nav
        class="flex gap-2 text-[0.65rem] font-bold text-on-surface-variant mb-2 uppercase tracking-[0.15em]"
      >
        <span>Production Cluster</span>
        <span class="text-outline-variant opacity-40">/</span>
        <span class="text-primary">Schemas</span>
      </nav>
      <h2 class="text-4xl font-black text-on-surface tracking-tighter">Database Blueprint</h2>
    </div>

    <div class="flex-1 flex gap-8">
      <div class="w-64 space-y-6">
        <div>
          <h3
            class="text-[0.6rem] font-black text-on-surface-variant uppercase tracking-widest mb-4 opacity-60"
          >
            Available Schemas
          </h3>
          <div class="space-y-1">
            <button
              v-for="schema in schemas"
              :key="schema.name"
              @click="selectSchema(schema)"
              class="w-full flex items-center justify-between px-4 py-3 rounded-xl transition-all group"
              :class="
                selectedSchema.name === schema.name
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
          </div>
        </div>
      </div>

      <div
        class="flex-1 bg-surface-container-lowest rounded-3xl shadow-ambient p-8 overflow-y-auto"
      >
        <div class="flex justify-between items-start mb-8">
          <div>
            <h4 class="text-2xl font-black text-on-surface tracking-tight">
              {{ selectedSchema.name }}.{{ selectedTable }}
            </h4>
            <p class="text-xs text-on-surface-variant font-medium mt-1 uppercase tracking-wider">
              Relation: Base Table • 1.2M Rows
            </p>
          </div>
          <div class="flex gap-2">
            <button
              class="p-2 hover:bg-surface-container-high rounded-lg text-on-surface-variant transition-colors"
            >
              <span class="material-symbols-outlined">edit</span>
            </button>
            <button
              class="p-2 hover:bg-surface-container-high rounded-lg text-on-surface-variant transition-colors"
            >
              <span class="material-symbols-outlined">refresh</span>
            </button>
          </div>
        </div>

        <table class="w-full text-left">
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
                Constraints
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-surface-variant/5">
            <tr class="group hover:bg-surface-container-low/30 transition-colors">
              <td class="py-4">
                <div class="flex items-center gap-2">
                  <span class="material-symbols-outlined text-sm text-primary">key</span>
                  <span class="text-sm font-bold text-on-surface">id</span>
                </div>
              </td>
              <td class="py-4 font-mono text-xs text-on-surface-variant uppercase tracking-tighter">
                uuid
              </td>
              <td class="py-4">
                <span
                  class="px-2 py-0.5 bg-secondary-container text-on-secondary-container rounded text-[0.6rem] font-black uppercase tracking-tighter"
                  >Primary Key</span
                >
              </td>
            </tr>
            <tr class="group hover:bg-surface-container-low/30 transition-colors">
              <td class="py-4">
                <div class="flex items-center gap-2 ml-6">
                  <span class="text-sm font-bold text-on-surface">created_at</span>
                </div>
              </td>
              <td class="py-4 font-mono text-xs text-on-surface-variant uppercase tracking-tighter">
                timestamp
              </td>
              <td class="py-4 text-xs text-on-surface-variant font-medium italic">default now()</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
