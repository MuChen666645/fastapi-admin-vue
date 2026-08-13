<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { NLayout, NLayoutContent } from 'naive-ui'
import { RouterView } from 'vue-router'

import ContentLoading from '@/components/ContentLoading/index.vue'
import { useLayoutSettingsStore } from '@/stores'
import AppFooter from './components/AppFooter/index.vue'
import AppHeader from './components/AppHeader/index.vue'
import AppSidebar from './components/AppSidebar/index.vue'
import AppTabs from './components/AppTabs/index.vue'
import SystemSettingsDrawer from './components/SystemSettingsDrawer/index.vue'
import { useRouteCache } from '@/hooks/useRouteCache'

defineOptions({ name: 'BasicLayout' })

const sidebarCollapsed = ref(false)
const routeViewKey = ref(0)
const systemSettingsVisible = ref(false)
const layoutSettings = useLayoutSettingsStore()
const { cachedComponentNames, getCachedRouteComponent, getRouteKey } = useRouteCache()
const layoutTransitionDuration = {
  enter: 180,
  leave: 180,
} as const
const layoutClasses = computed(() => ({
  'basic-layout--content-scroll': layoutSettings.scrollMode === 'content',
  'basic-layout--workspace-scroll': layoutSettings.scrollMode === 'workspace',
  'basic-layout--sticky-nav': layoutSettings.scrollMode === 'sticky',
}))
const mainLayoutShellClasses = computed(() => ({
  'main-layout-shell--without-tabs': !layoutSettings.showTabs,
  'main-layout-shell--without-footer': !layoutSettings.showFooter,
}))

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

const openSystemSettings = (): void => {
  systemSettingsVisible.value = true
}
</script>

<template>
  <NLayout has-sider class="basic-layout" :class="layoutClasses">
    <AppSidebar v-if="layoutSettings.showSidebar" v-model:collapsed="sidebarCollapsed" />
    <div class="main-layout-shell" :class="mainLayoutShellClasses">
      <NLayout class="main-layout">
        <AppHeader
          v-model:sidebar-collapsed="sidebarCollapsed"
          :show-breadcrumb="layoutSettings.showBreadcrumb"
          @open-system-settings="openSystemSettings"
        />
        <AppTabs v-if="layoutSettings.showTabs" @refresh="refreshRouteView" />
        <NLayoutContent class="layout-content" :native-scrollbar="false">
          <div class="layout-content__body">
            <main
              class="content-container mx-auto w-full"
              :class="{ 'content-container--centered': layoutSettings.contentWidth === 'centered' }"
            >
              <RouterView v-slot="{ Component, route: viewRoute }">
                <Transition name="layout-page" mode="out-in" :duration="layoutTransitionDuration">
                  <KeepAlive :include="cachedComponentNames">
                    <component
                      v-if="Component"
                      :is="getCachedRouteComponent(Component, viewRoute)"
                      :key="`${getRouteKey(viewRoute)}:${routeViewKey}`"
                    />
                  </KeepAlive>
                </Transition>
              </RouterView>
            </main>
          </div>
        </NLayoutContent>
        <AppFooter v-if="layoutSettings.showFooter" />
      </NLayout>
      <div class="content-loading-viewport" data-testid="content-loading-viewport">
        <ContentLoading />
      </div>
      <SystemSettingsDrawer v-model:show="systemSettingsVisible" />
    </div>
  </NLayout>
</template>

<style lang="scss" scoped>
.main-layout-shell {
  --layout-loading-top: calc(var(--app-layout-header-height) + var(--app-layout-tabs-height));
  --layout-loading-bottom: var(--app-layout-footer-height);

  position: relative;
  width: 100%;
  height: 100%;
  min-width: 0;
  min-height: 0;
  flex: 1 1 auto;
  isolation: isolate;
  overflow: hidden;
}

.main-layout-shell--without-tabs {
  --layout-loading-top: var(--app-layout-header-height);
}

.main-layout-shell--without-footer {
  --layout-loading-bottom: 0px;
}

.content-loading-viewport {
  position: absolute;
  z-index: 20;
  inset: var(--layout-loading-top) 0 var(--layout-loading-bottom);
  pointer-events: none;
}

.layout-content__body {
  min-height: 100%;
}
</style>
