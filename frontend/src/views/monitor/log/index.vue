<script setup lang="ts">
import { NCard, NEmpty } from 'naive-ui'

defineOptions({ name: 'MonitorLogView' })
</script>

<template>
  <section class="page-shell">
    <NCard bordered class="page-card">
      <p class="page-kicker">系统监控</p>
      <h1 class="page-title">日志管理</h1>
      <NEmpty description="暂无日志数据" />
    </NCard>
  </section>
</template>

<style scoped>
.page-shell {
  max-width: 1040px;
}

.page-card {
  border-radius: 10px;
}

.page-kicker {
  margin: 0 0 8px;
  color: var(--app-color-primary);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.page-title {
  margin: 0 0 40px;
  font-size: 26px;
}
</style>
