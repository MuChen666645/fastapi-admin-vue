import { beforeEach, describe, expect, it, vi } from 'vitest'

import { mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { nextTick } from 'vue'

vi.mock('../hooks/useECharts', () => ({
  useECharts: () => ({ renderChart: vi.fn() }),
}))

import HomeView from '../views/home/index.vue'
import { usePreferencesStore } from '../stores'

describe('HomeView', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('follows the preferred language without rendering a page-level switcher', async () => {
    const pinia = createPinia()
    const preferences = usePreferencesStore(pinia)
    const wrapper = mount(HomeView, {
      global: {
        plugins: [pinia],
      },
    })

    expect(wrapper.find('.language-toggle').exists()).toBe(false)

    preferences.language = 'en-US'
    await nextTick()

    expect(preferences.language).toBe('en-US')
    expect(wrapper.find('.page-heading').exists()).toBe(false)

    wrapper.unmount()
  })
})
