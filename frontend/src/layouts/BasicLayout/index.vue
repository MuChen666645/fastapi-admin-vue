<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { NLayout, NLayoutContent } from 'naive-ui'
import { RouterView } from 'vue-router'

import ContentLoading from '@/components/ContentLoading/index.vue'
import AppFooter from './components/AppFooter/index.vue'
import AppHeader from './components/AppHeader/index.vue'
import AppSidebar from './components/AppSidebar/index.vue'
import AppTabs from './components/AppTabs/index.vue'
import { useRouteCache } from '@/hooks/useRouteCache'

defineOptions({ name: 'BasicLayout' })

const sidebarCollapsed = ref(false)
const routeViewKey = ref(0)
const { cachedComponentNames, getCachedRouteComponent, getRouteKey } = useRouteCache()

const syncSidebarForViewport = (): void => {
  if (typeof window.matchMedia !== 'function') {
    return
  }

  sidebarCollapsed.value = window.matchMedia('(max-width: 900px)').matches
}

onMounted(() => {
  syncSidebarForViewport()
  window.addEventListener('resize', syncSidebarForViewport)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', syncSidebarForViewport)
})

const refreshRouteView = (): void => {
  routeViewKey.value += 1
}
</script>

<template>
  <NLayout has-sider class="basic-layout">
    <AppSidebar v-model:collapsed="sidebarCollapsed" />
    <NLayout class="main-layout">
      <AppHeader v-model:sidebar-collapsed="sidebarCollapsed" />
      <AppTabs @refresh="refreshRouteView" />
      <NLayoutContent class="layout-content" :native-scrollbar="false">
        <div class="layout-content__body">
          <ContentLoading />
          <main class="content-container mx-auto w-full">
            <RouterView v-slot="{ Component, route: viewRoute }">
              <KeepAlive :include="cachedComponentNames">
                <component
                  :is="getCachedRouteComponent(Component, viewRoute)"
                  :key="`${getRouteKey(viewRoute)}:${routeViewKey}`"
                />
              </KeepAlive>
            </RouterView>
          </main>
        </div>
      </NLayoutContent>
      <AppFooter />
    </NLayout>
  </NLayout>
</template>

<style scoped>
.layout-content__body {
  position: relative;
  min-height: 100%;
}
</style>
