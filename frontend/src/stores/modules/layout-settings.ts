import { ref } from 'vue'
import { defineStore } from 'pinia'

import type { LayoutSettings } from '@/types'

const defaultLayoutSettings: LayoutSettings = {
  contentWidth: 'full',
  showSidebar: true,
  showTabs: true,
  showBreadcrumb: true,
  showFooter: true,
  scrollMode: 'content',
}

export const useLayoutSettingsStore = defineStore(
  'layout-settings',
  () => {
    const contentWidth = ref(defaultLayoutSettings.contentWidth)
    const showSidebar = ref(defaultLayoutSettings.showSidebar)
    const showTabs = ref(defaultLayoutSettings.showTabs)
    const showBreadcrumb = ref(defaultLayoutSettings.showBreadcrumb)
    const showFooter = ref(defaultLayoutSettings.showFooter)
    const scrollMode = ref(defaultLayoutSettings.scrollMode)

    const reset = (): void => {
      contentWidth.value = defaultLayoutSettings.contentWidth
      showSidebar.value = defaultLayoutSettings.showSidebar
      showTabs.value = defaultLayoutSettings.showTabs
      showBreadcrumb.value = defaultLayoutSettings.showBreadcrumb
      showFooter.value = defaultLayoutSettings.showFooter
      scrollMode.value = defaultLayoutSettings.scrollMode
    }

    return {
      contentWidth,
      showSidebar,
      showTabs,
      showBreadcrumb,
      showFooter,
      scrollMode,
      reset,
    }
  },
  {
    persist: {
      storage: localStorage,
      pick: [
        'contentWidth',
        'showSidebar',
        'showTabs',
        'showBreadcrumb',
        'showFooter',
        'scrollMode',
      ],
    },
  },
)
