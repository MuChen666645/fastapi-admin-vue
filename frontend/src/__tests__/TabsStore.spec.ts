import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import { createApp } from 'vue'
import { afterEach, beforeEach, describe, expect, it } from 'vitest'

import { createPinia, setActivePinia } from 'pinia'

import { useTabsStore } from '../stores'
import type { AppTab } from '../types'

const createTab = (key: string, closable = true, icon: string | null = null): AppTab => ({
  key,
  title: key,
  fullPath: `/${key}`,
  icon,
  cacheName: `DynamicRoute_${key}`,
  cacheable: key !== 'home',
  closable,
})

const createPersistedPinia = () => {
  const app = createApp({ render: () => null })
  const pinia = createPinia().use(piniaPluginPersistedstate)
  app.use(pinia)
  app.mount(document.createElement('div'))
  return { app, pinia }
}

describe('tabs store', () => {
  beforeEach(() => {
    sessionStorage.clear()
  })

  afterEach(() => {
    sessionStorage.clear()
  })

  it('keeps the first route as a fixed tab', () => {
    setActivePinia(createPinia())
    const tabs = useTabsStore()

    tabs.addTab(createTab('home', false, 'HomeOutline'))
    tabs.addTab(createTab('users', true, 'PeopleOutline'))

    expect(tabs.tabs.map((tab) => [tab.key, tab.icon, tab.closable])).toEqual([
      ['home', 'HomeOutline', false],
      ['users', 'PeopleOutline', true],
    ])
  })

  it('supports closing current, other and all tabs while preserving the fixed tab', () => {
    setActivePinia(createPinia())
    const tabs = useTabsStore()

    tabs.addTab(createTab('home'))
    tabs.addTab(createTab('users'))
    tabs.addTab(createTab('roles'))

    tabs.closeOthers('roles')
    expect(tabs.tabs.map((tab) => tab.key)).toEqual(['home', 'roles'])

    tabs.removeTab('roles')
    expect(tabs.tabs.map((tab) => tab.key)).toEqual(['home'])

    tabs.addTab(createTab('users'))
    tabs.closeAll()
    expect(tabs.tabs.map((tab) => tab.key)).toEqual(['home'])
  })

  it('exposes cacheable component names and removes them with closed tabs', () => {
    setActivePinia(createPinia())
    const tabs = useTabsStore()

    tabs.addTab(createTab('home'))
    tabs.addTab(createTab('users'))
    tabs.addTab({ ...createTab('roles'), cacheable: false })

    expect(tabs.cachedComponentNames).toEqual(['DynamicRoute_users'])

    tabs.removeTab('users')
    expect(tabs.cachedComponentNames).toEqual([])
  })

  it('restores tab data from session storage after a page refresh', () => {
    const firstApp = createPersistedPinia()
    setActivePinia(firstApp.pinia)
    const tabs = useTabsStore()

    tabs.addTab(createTab('home', false, 'HomeOutline'))
    tabs.addTab(createTab('users', true, 'PeopleOutline'))

    const restoredApp = createPersistedPinia()
    setActivePinia(restoredApp.pinia)
    const restoredTabs = useTabsStore()

    expect(restoredTabs.tabs.map((tab) => [tab.key, tab.icon, tab.closable])).toEqual([
      ['home', 'HomeOutline', false],
      ['users', 'PeopleOutline', true],
    ])

    restoredTabs.reset()
    expect(restoredTabs.tabs).toEqual([])

    firstApp.app.unmount()
    restoredApp.app.unmount()
  })
})
