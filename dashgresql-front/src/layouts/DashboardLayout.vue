<script setup>
import { RouterView, useRouter } from 'vue-router'
const router = useRouter()

const logout = () => {
  localStorage.removeItem('dashgresql_auth')
  router.push('/login')
}
</script>

<template>
  <div
    class="min-h-screen bg-surface font-body text-on-surface selection:bg-primary-container selection:text-on-primary-container"
  >
    <aside
      class="h-screen w-64 fixed left-0 top-0 z-50 bg-surface-container-low flex flex-col p-4 gap-y-2"
    >
      <div class="flex items-center gap-3 px-2 py-6 mb-4">
        <div
          class="w-10 h-10 rounded-lg bg-primary flex items-center justify-center text-on-primary"
        >
          <span class="material-symbols-outlined">database</span>
        </div>
        <div>
          <h2 class="text-primary font-black tracking-tight leading-none text-sm">
            Production Cluster
          </h2>
          <p
            class="text-[0.7rem] text-on-surface-variant font-medium mt-1 uppercase tracking-wider"
          >
            v15.4 • Running
          </p>
        </div>
      </div>

      <nav class="flex-1 space-y-1 px-4">
        <RouterLink
          to="/"
          class="flex items-center gap-3 px-3 py-2.5 rounded-md transition-all duration-200"
          :class="
            $route.path === '/'
              ? 'text-primary font-bold bg-surface-container-lowest shadow-sm'
              : 'text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high'
          "
        >
          <span class="material-symbols-outlined text-[1.25rem]">database</span>
          <span class="text-sm">Databases</span>
        </RouterLink>

        <RouterLink
          to="/"
          class="flex items-center gap-3 px-3 py-2.5 text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high rounded-md transition-all duration-200 group"
        >
          <span class="material-symbols-outlined text-[1.25rem] group-hover:text-primary"
            >terminal</span
          >
          <span class="text-sm font-medium">Query Console</span>
        </RouterLink>

        <RouterLink
          to="/"
          class="flex items-center gap-3 px-3 py-2.5 text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high rounded-md transition-all duration-200 group"
        >
          <span class="material-symbols-outlined text-[1.25rem] group-hover:text-primary"
            >schema</span
          >
          <span class="text-sm font-medium">Schemas</span>
        </RouterLink>

        <RouterLink
          to="/"
          class="flex items-center gap-3 px-3 py-2.5 text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high rounded-md transition-all duration-200 group"
        >
          <span class="material-symbols-outlined text-[1.25rem] group-hover:text-primary"
            >sync_alt</span
          >
          <span class="text-sm font-medium">Replication</span>
        </RouterLink>

        <RouterLink
          to="/"
          class="flex items-center gap-3 px-3 py-2.5 text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high rounded-md transition-all duration-200 group"
        >
          <span class="material-symbols-outlined text-[1.25rem] group-hover:text-primary"
            >list_alt</span
          >
          <span class="text-sm font-medium">Logs</span>
        </RouterLink>
      </nav>

      <div class="mt-auto pt-4 border-t border-surface-variant/20 px-4 pb-6 space-y-1">
        <a
          href="#"
          class="flex items-center gap-3 px-3 py-2 text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high rounded-md transition-all text-xs font-bold uppercase tracking-wider"
        >
          <span class="material-symbols-outlined text-[1rem]">help</span>
          <span>Docs</span>
        </a>
        <RouterLink
          to="/logout"
          class="flex items-center gap-3 px-3 py-2 text-on-surface-variant hover:text-error hover:bg-error-container/10 rounded-md transition-all text-xs font-bold uppercase tracking-wider"
        >
          <span class="material-symbols-outlined text-[1rem]">logout</span>
          <span>Terminate</span>
        </RouterLink>
      </div>
    </aside>

    <main class="ml-64 min-h-screen flex flex-col">
      <header
        class="h-16 sticky top-0 z-40 bg-surface-container-low flex justify-between items-center px-8"
      >
        <div class="flex items-center gap-8">
          <h1 class="text-lg font-bold tracking-tighter text-on-surface">Dashgresql</h1>
          <div class="relative w-96">
            <span
              class="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-on-surface-variant text-sm"
              >search</span
            >
            <input
              class="w-full bg-surface-container-lowest border-none rounded-md py-2 pl-10 pr-4 text-sm focus:ring-2 focus:ring-primary/20 outline-none"
              placeholder="Search resources..."
              type="text"
            />
          </div>
        </div>

        <div class="flex items-center gap-4">
          <button
            class="p-2 text-on-surface-variant hover:bg-surface-container-high rounded-full transition-colors"
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
              @click="logout"
              class="p-2 text-on-surface-variant hover:text-error hover:bg-error-container/10 rounded-full transition-colors"
              title="Logout"
            >
              <span class="material-symbols-outlined">logout</span>
            </button>
          </div>
        </div>
      </header>

      <div class="p-8 flex-1">
        <RouterView />
      </div>
    </main>
  </div>
</template>
