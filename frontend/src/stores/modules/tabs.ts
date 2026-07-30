import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import type { AppTab } from '@/types'

export const useTabsStore = defineStore('tabs', () => {
  const tabs = ref<AppTab[]>([])
  const cachedComponentNames = computed(() =>
    tabs.value.flatMap((tab) => (tab.cacheable && tab.cacheName ? [tab.cacheName] : [])),
  )

  const addTab = (tab: AppTab): void => {
    const existingTab = tabs.value.find((item) => item.key === tab.key)
    if (existingTab) {
      existingTab.fullPath = tab.fullPath
      existingTab.title = tab.title
      existingTab.icon = tab.icon
      existingTab.cacheName = tab.cacheName
      existingTab.cacheable = tab.cacheable
      return
    }

    tabs.value.push({
      ...tab,
      closable: tabs.value.length > 0 && tab.closable,
    })
  }

  const removeTab = (key: string): void => {
    const tab = tabs.value.find((item) => item.key === key)
    if (!tab?.closable) {
      return
    }

    tabs.value = tabs.value.filter((item) => item.key !== key)
  }

  const closeOthers = (key: string): void => {
    tabs.value = tabs.value.filter((tab) => !tab.closable || tab.key === key)
  }

  const closeAll = (): void => {
    tabs.value = tabs.value.filter((tab) => !tab.closable)
  }

  const reset = (): void => {
    tabs.value = []
  }

  return {
    tabs,
    cachedComponentNames,
    addTab,
    removeTab,
    closeOthers,
    closeAll,
    reset,
  }
})
