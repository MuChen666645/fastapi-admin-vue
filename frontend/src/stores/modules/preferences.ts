import { reactive, toRefs } from 'vue'
import { defineStore } from 'pinia'

import type { PreferencesSettings } from '@/types'

const defaultPreferences: PreferencesSettings = {
  themeMode: 'light',
  accentColor: 'blue',
  radiusScale: 0.5,
  fontSize: 16,
  colorWeakMode: false,
  grayscaleMode: false,
  language: 'zh-CN',
  timezone: 'Asia/Shanghai',
  dynamicTitle: true,
  watermark: false,
  autoUpdate: true,
  pageTransition: true,
  loadingAnimation: true,
  contentWidth: 'full',
  showSidebar: true,
  showTabs: true,
  showBreadcrumb: true,
  showFooter: true,
  scrollMode: 'content',
}

export const usePreferencesStore = defineStore(
  'preferences',
  () => {
    const settings = reactive<PreferencesSettings>({ ...defaultPreferences })

    const reset = (): void => {
      Object.assign(settings, defaultPreferences)
    }

    return {
      ...toRefs(settings),
      reset,
    }
  },
  {
    persist: {
      storage: localStorage,
      pick: Object.keys(defaultPreferences),
    },
  },
)
