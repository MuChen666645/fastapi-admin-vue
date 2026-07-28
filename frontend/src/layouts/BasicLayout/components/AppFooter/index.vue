<script setup lang="ts">
import { NLayoutFooter, NText } from 'naive-ui'

defineOptions({ name: 'AppFooter' })

const appTitle = import.meta.env.VITE_APP_TITLE || 'FastAPI Admin'
const currentYear = new Date().getFullYear()
</script>

<template>
  <NLayoutFooter class="app-footer" bordered>
    <NText depth="3">{{ appTitle }}</NText>
    <NText depth="3">API v1 · {{ currentYear }}</NText>
  </NLayoutFooter>
</template>

<style scoped>
.app-footer {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 20px 32px;
  background: var(--app-color-surface);
  border-top: 1px solid var(--app-color-border);
  font-size: 12px;
  box-sizing: border-box;
}

@media (width <= 768px) {
  .app-footer {
    flex-wrap: wrap;
    padding: 14px 16px;
  }
}
</style>
