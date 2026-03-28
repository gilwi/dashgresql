<script setup>
defineProps(['show', 'title'])
defineEmits(['close'])
</script>

<template>
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="show" class="fixed inset-0 z-[100] flex items-center justify-center p-6">
        <div
          class="absolute inset-0 bg-on-surface/20 backdrop-blur-sm"
          @click="$emit('close')"
        ></div>

        <div
          class="relative w-full max-w-lg bg-surface-container-lowest/90 backdrop-blur-xl p-10 rounded-3xl shadow-ambient border border-white/20"
        >
          <div class="flex justify-between items-center mb-8">
            <h3 class="text-xl font-bold tracking-tight text-on-surface">{{ title }}</h3>
            <button
              @click="$emit('close')"
              class="text-on-surface-variant hover:text-primary transition-colors"
            >
              <span class="material-symbols-outlined">close</span>
            </button>
          </div>

          <slot></slot>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
