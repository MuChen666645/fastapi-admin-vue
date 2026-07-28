<script setup lang="ts">
import { ref } from 'vue'
import { NLayout, NLayoutContent } from 'naive-ui'
import { RouterView } from 'vue-router'

import AppFooter from './components/AppFooter/index.vue'
import AppHeader from './components/AppHeader/index.vue'
import AppSidebar from './components/AppSidebar/index.vue'

defineOptions({ name: 'BasicLayout' })

const sidebarCollapsed = ref(false)
</script>

<template>
  <NLayout has-sider class="basic-layout min-h-screen">
    <AppSidebar v-model:collapsed="sidebarCollapsed" />
    <NLayout class="main-layout">
      <AppHeader v-model:sidebar-collapsed="sidebarCollapsed" />
      <NLayoutContent class="layout-content">
        <main class="content-container mx-auto w-full">
          <RouterView />
        </main>
      </NLayoutContent>
      <AppFooter />
    </NLayout>
  </NLayout>
</template>

<style scoped>
.basic-layout {
  background: var(--app-color-page);
}

.main-layout {
  min-width: 0;
  background: var(--app-color-page);
}

.layout-content {
  min-height: calc(100vh - 125px);
  background: var(--app-color-page);
}

.content-container {
  min-height: calc(100vh - 128px);
  padding: 24px 32px 40px;
}

@media (width <= 768px) {
  .content-container {
    padding: 20px 16px 32px;
  }
}
</style>
