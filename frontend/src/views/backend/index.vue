<script setup lang="ts">
import { NCard, NDescriptions, NDescriptionsItem, NEmpty, NText } from 'naive-ui'
import { useRoute } from 'vue-router'

defineOptions({ name: 'BackendModuleView' })

const route = useRoute()
</script>

<template>
  <section class="module-page">
    <NCard bordered class="module-card">
      <div class="module-heading">
        <div>
          <NText class="module-kicker">服务端菜单</NText>
          <NText tag="h1" class="module-title" strong>{{ route.meta.title }}</NText>
        </div>
        <span class="module-status">已授权</span>
      </div>
      <NDescriptions :column="1" label-placement="left" bordered>
        <NDescriptionsItem label="路由名称">{{ route.name }}</NDescriptionsItem>
        <NDescriptionsItem label="组件标识">{{
          route.meta.serverComponent || '目录节点'
        }}</NDescriptionsItem>
        <NDescriptionsItem label="访问路径">{{ route.fullPath }}</NDescriptionsItem>
      </NDescriptions>
      <NEmpty class="module-empty" description="该菜单已由服务端授权，业务模块正在接入中" />
    </NCard>
  </section>
</template>

<style scoped>
.module-page {
  max-width: 1040px;
}

.module-card {
  border-radius: 10px;
}

.module-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 24px;
}

.module-kicker {
  display: block;
  margin-bottom: 8px;
  color: var(--app-color-primary);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.module-title {
  margin: 0;
  font-size: 26px;
}

.module-status {
  padding: 5px 10px;
  color: var(--app-color-success);
  border: 1px solid rgb(39 125 87 / 20%);
  border-radius: 999px;
  background: rgb(39 125 87 / 8%);
  font-size: 12px;
  font-weight: 700;
}

.module-empty {
  padding: 48px 0 22px;
}
</style>
