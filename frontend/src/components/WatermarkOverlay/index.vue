<script setup lang="ts">
import { computed } from 'vue'

import { useAuthStore, usePreferencesStore } from '@/stores'

defineOptions({ name: 'WatermarkOverlay' })

const auth = useAuthStore()
const preferences = usePreferencesStore()
const visible = computed(() => preferences.watermark && auth.isAuthenticated)
const watermarkItems = Array.from({ length: 18 }, (_, index) => index)
</script>

<template>
  <div v-if="visible" class="watermark-overlay" aria-hidden="true">
    <span v-for="item in watermarkItems" :key="item">{{ auth.displayName }}</span>
  </div>
</template>

<style scoped>
.watermark-overlay {
  position: fixed;
  z-index: 1500;
  inset: 0;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  align-content: space-around;
  gap: 56px 10vw;
  padding: 5vh 5vw;
  overflow: hidden;
  pointer-events: none;
  user-select: none;
}

.watermark-overlay span {
  color: rgb(52 68 93 / 8%);
  font-size: 18px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-align: center;
  transform: rotate(-24deg);
}

.app-root--dark .watermark-overlay span {
  color: rgb(255 255 255 / 8%);
}

@media (width <= 700px) {
  .watermark-overlay {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
