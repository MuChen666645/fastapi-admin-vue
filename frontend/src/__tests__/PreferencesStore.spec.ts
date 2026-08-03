import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import { createApp } from 'vue'
import { afterEach, beforeEach, describe, expect, it } from 'vitest'

import { createPinia } from 'pinia'

import { usePreferencesStore } from '../stores'

const createPersistedPinia = () => {
  const app = createApp({ render: () => null })
  const pinia = createPinia().use(piniaPluginPersistedstate)
  app.use(pinia)
  app.mount(document.createElement('div'))
  return { app, pinia }
}

describe('preferences store', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  afterEach(() => {
    localStorage.clear()
  })

  it('persists appearance, language, feedback, and scroll preferences', () => {
    const firstApp = createPersistedPinia()
    const firstPreferences = usePreferencesStore(firstApp.pinia)

    firstPreferences.themeMode = 'dark'
    firstPreferences.accentColor = 'rose'
    firstPreferences.radiusScale = 1
    firstPreferences.fontSize = 18
    firstPreferences.language = 'en-US'
    firstPreferences.watermark = true
    firstPreferences.loadingAnimation = false
    firstPreferences.scrollMode = 'workspace'

    const restoredApp = createPersistedPinia()
    const restoredPreferences = usePreferencesStore(restoredApp.pinia)

    expect(restoredPreferences.themeMode).toBe('dark')
    expect(restoredPreferences.accentColor).toBe('rose')
    expect(restoredPreferences.radiusScale).toBe(1)
    expect(restoredPreferences.fontSize).toBe(18)
    expect(restoredPreferences.language).toBe('en-US')
    expect(restoredPreferences.watermark).toBe(true)
    expect(restoredPreferences.loadingAnimation).toBe(false)
    expect(restoredPreferences.scrollMode).toBe('workspace')

    restoredPreferences.reset()
    expect(restoredPreferences.themeMode).toBe('light')
    expect(restoredPreferences.language).toBe('zh-CN')
    expect(restoredPreferences.scrollMode).toBe('content')

    firstApp.app.unmount()
    restoredApp.app.unmount()
  })
})
