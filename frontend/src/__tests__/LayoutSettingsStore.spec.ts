import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import { createApp } from 'vue'
import { afterEach, beforeEach, describe, expect, it } from 'vitest'

import { createPinia } from 'pinia'

import { useLayoutSettingsStore } from '../stores'

const createPersistedPinia = () => {
  const app = createApp({ render: () => null })
  const pinia = createPinia().use(piniaPluginPersistedstate)
  app.use(pinia)
  app.mount(document.createElement('div'))
  return { app, pinia }
}

describe('layout settings store', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  afterEach(() => {
    localStorage.clear()
  })

  it('persists layout preferences and restores the defaults', () => {
    const firstApp = createPersistedPinia()
    const firstSettings = useLayoutSettingsStore(firstApp.pinia)

    firstSettings.contentWidth = 'centered'
    firstSettings.showSidebar = false
    firstSettings.scrollMode = 'sticky'

    const restoredApp = createPersistedPinia()
    const restoredSettings = useLayoutSettingsStore(restoredApp.pinia)

    expect(restoredSettings.contentWidth).toBe('centered')
    expect(restoredSettings.showSidebar).toBe(false)
    expect(restoredSettings.scrollMode).toBe('sticky')

    restoredSettings.reset()
    expect(restoredSettings.contentWidth).toBe('full')
    expect(restoredSettings.showSidebar).toBe(true)
    expect(restoredSettings.scrollMode).toBe('content')

    firstApp.app.unmount()
    restoredApp.app.unmount()
  })
})
