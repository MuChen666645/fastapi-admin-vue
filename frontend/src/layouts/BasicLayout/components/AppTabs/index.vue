<script setup lang="ts">
import { computed, nextTick, reactive, ref, watch } from 'vue'
import {
  ChevronBackOutline,
  ChevronForwardOutline,
  CloseOutline,
  EllipsisHorizontalOutline,
  HomeOutline,
  RefreshOutline,
} from '@vicons/ionicons5'
import { NDropdown, NIcon } from 'naive-ui'
import { useRoute, useRouter } from 'vue-router'

import { useLocale } from '@/hooks'
import { resolveIconComponent } from '@/hooks/useIcon'
import { getRouteCacheName } from '@/router/route-cache'
import { useTabsStore } from '@/stores'
import type { AppTab } from '@/types'
import { translateMenuTitle } from '@/utils/i18n'

defineOptions({ name: 'AppTabs' })

const emit = defineEmits<{
  refresh: []
}>()

const route = useRoute()
const router = useRouter()
const tabsStore = useTabsStore()
const { language, t } = useLocale()
const tabsContainer = ref<HTMLDivElement | null>(null)
const contextMenu = reactive({
  visible: false,
  x: 0,
  y: 0,
  tabKey: '',
})

const activeTabKey = computed(() => String(route.name ?? route.path))
const contextTab = computed(() => tabsStore.tabs.find((tab) => tab.key === contextMenu.tabKey))

const getTabIcon = (tab: AppTab) => resolveIconComponent(tab.icon)
const getTabTitle = (tab: AppTab): string => translateMenuTitle(tab.title, language.value)

const contextMenuOptions = computed(() => [
  { label: t('tabs.refreshCurrent'), key: 'refresh' },
  {
    label: t('tabs.close').replace('{title}', contextTab.value?.title ?? ''),
    key: 'close',
    disabled: !contextTab.value?.closable,
  },
  { type: 'divider', key: 'divider' },
  { label: t('tabs.closeOther'), key: 'close-others' },
  { label: t('tabs.closeAll'), key: 'close-all' },
])

const topMenuOptions = computed(() => [
  { label: t('tabs.refreshCurrent'), key: 'refresh' },
  { label: t('tabs.closeOther'), key: 'close-others' },
  { label: t('tabs.closeAll'), key: 'close-all' },
])

const syncCurrentTab = (): void => {
  const title = String(route.meta.title ?? route.name ?? route.path)
  const icon = typeof route.meta.icon === 'string' ? route.meta.icon : null
  tabsStore.addTab({
    key: activeTabKey.value,
    title,
    fullPath: route.fullPath,
    icon,
    cacheName: route.meta.noCache === false ? getRouteCacheName(activeTabKey.value) : null,
    cacheable: route.meta.noCache === false,
    closable: true,
  })
}

watch(
  () => [route.name, route.path, route.fullPath, route.meta.title, route.meta.icon] as const,
  syncCurrentTab,
  { immediate: true },
)

const hideContextMenu = (): void => {
  contextMenu.visible = false
  contextMenu.tabKey = ''
}

const openContextMenu = (event: MouseEvent, tab: AppTab): void => {
  contextMenu.tabKey = tab.key
  contextMenu.x = event.clientX
  contextMenu.y = event.clientY
  contextMenu.visible = true
}

const scrollTabs = (distance: number): void => {
  tabsContainer.value?.scrollBy({ left: distance, behavior: 'smooth' })
}

const navigateToTab = async (tab: AppTab | undefined): Promise<void> => {
  if (tab && tab.fullPath !== route.fullPath) {
    await router.push(tab.fullPath)
  }
}

const closeTab = async (key: string): Promise<void> => {
  const tabIndex = tabsStore.tabs.findIndex((tab) => tab.key === key)
  const tab = tabsStore.tabs[tabIndex]
  if (!tab?.closable) {
    return
  }

  const isActive = activeTabKey.value === key
  tabsStore.removeTab(key)
  if (!isActive) {
    return
  }

  const nextTab = tabsStore.tabs[tabIndex - 1] ?? tabsStore.tabs[tabIndex] ?? tabsStore.tabs[0]
  await navigateToTab(nextTab)
}

const closeOtherTabs = async (key: string): Promise<void> => {
  const targetTab = tabsStore.tabs.find((tab) => tab.key === key)
  tabsStore.closeOthers(key)
  await navigateToTab(targetTab)
}

const closeAllTabs = async (): Promise<void> => {
  tabsStore.closeAll()
  await navigateToTab(tabsStore.tabs[0])
}

const refreshCurrentTab = async (key: string = activeTabKey.value): Promise<void> => {
  const targetTab = tabsStore.tabs.find((tab) => tab.key === key)
  await navigateToTab(targetTab)
  await nextTick()
  emit('refresh')
}

const handleMenuSelect = async (key: string | number): Promise<void> => {
  const menuKey = String(key)
  const targetKey = contextMenu.tabKey || activeTabKey.value
  hideContextMenu()

  if (menuKey === 'refresh') {
    await refreshCurrentTab(targetKey)
    return
  }

  if (menuKey === 'close') {
    await closeTab(targetKey)
    return
  }

  if (menuKey === 'close-others') {
    await closeOtherTabs(targetKey)
    return
  }

  if (menuKey === 'close-all') {
    await closeAllTabs()
  }
}

const handleTopMenuSelect = async (key: string | number): Promise<void> => {
  const menuKey = String(key)
  if (menuKey === 'refresh') {
    await refreshCurrentTab()
    return
  }

  if (menuKey === 'close-others') {
    await closeOtherTabs(activeTabKey.value)
    return
  }

  if (menuKey === 'close-all') {
    await closeAllTabs()
  }
}
</script>

<template>
  <section class="app-tabs" :aria-label="t('tabs.page')">
    <button
      type="button"
      class="tabs-scroll-button"
      :aria-label="t('tabs.scrollLeft')"
      :title="t('tabs.scrollLeft')"
      @click="scrollTabs(-180)"
    >
      <NIcon :size="16"><ChevronBackOutline /></NIcon>
    </button>

    <div ref="tabsContainer" class="tabs-list" role="tablist">
      <div
        v-for="tab in tabsStore.tabs"
        :key="tab.key"
        class="app-tab"
        :class="{ 'app-tab--active': activeTabKey === tab.key }"
        role="tab"
        :aria-selected="activeTabKey === tab.key"
        tabindex="0"
        @click="navigateToTab(tab)"
        @contextmenu.prevent="openContextMenu($event, tab)"
        @keydown.enter="navigateToTab(tab)"
      >
        <NIcon v-if="getTabIcon(tab)" :size="14" aria-hidden="true">
          <component :is="getTabIcon(tab)" />
        </NIcon>
        <NIcon v-else-if="!tab.closable" :size="14" aria-hidden="true">
          <HomeOutline />
        </NIcon>
        <span v-else class="tab-dot" aria-hidden="true" />
        <span class="app-tab-title">{{ getTabTitle(tab) }}</span>
        <button
          v-if="tab.closable"
          type="button"
          class="tab-close-button"
          :aria-label="t('tabs.close').replace('{title}', getTabTitle(tab))"
          :title="t('tabs.close').replace('{title}', getTabTitle(tab))"
          @click.stop="closeTab(tab.key)"
        >
          <NIcon :size="13"><CloseOutline /></NIcon>
        </button>
      </div>
    </div>

    <button
      type="button"
      class="tabs-scroll-button"
      :aria-label="t('tabs.scrollRight')"
      :title="t('tabs.scrollRight')"
      @click="scrollTabs(180)"
    >
      <NIcon :size="16"><ChevronForwardOutline /></NIcon>
    </button>

    <span class="tabs-divider" aria-hidden="true" />
    <button
      type="button"
      class="tabs-action-button"
      :aria-label="t('tabs.refresh')"
      :title="t('tabs.refresh')"
      @click="refreshCurrentTab()"
    >
      <NIcon :size="16"><RefreshOutline /></NIcon>
    </button>
    <NDropdown :options="topMenuOptions" trigger="click" @select="handleTopMenuSelect">
      <button
        type="button"
        class="tabs-action-button"
        :aria-label="t('tabs.operations')"
        :title="t('tabs.operations')"
      >
        <NIcon :size="17"><EllipsisHorizontalOutline /></NIcon>
      </button>
    </NDropdown>

    <NDropdown
      trigger="manual"
      placement="bottom-start"
      :show="contextMenu.visible"
      :x="contextMenu.x"
      :y="contextMenu.y"
      :options="contextMenuOptions"
      @select="handleMenuSelect"
      @clickoutside="hideContextMenu"
    />
  </section>
</template>
