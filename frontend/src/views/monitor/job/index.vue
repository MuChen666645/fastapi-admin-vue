<script setup lang="ts">
import { NCard, NEmpty } from 'naive-ui'

defineOptions({ name: 'MonitorJobView' })
</script>

<template>
  <section class="page-shell">
    <NCard bordered class="page-card">
      <NEmpty description="暂无定时任务数据" />
    </NCard>
  </section>
</template>

<style lang="scss" scoped>
.page-shell {
  max-width: 1040px;
}

.page-card {
  border-radius: 10px;
}
</style>
