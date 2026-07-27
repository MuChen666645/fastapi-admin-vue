import { describe, it, expect } from 'vitest'

import { flushPromises, mount } from '@vue/test-utils'
import { NLoadingBarProvider } from 'naive-ui'
import { nextTick } from 'vue'

import App from '../App.vue'
import RouterLoadingBar from '../components/RouterLoadingBar/index.vue'
import { createMockRouter } from './fixtures/mock-router'

describe('App', () => {
  it('mounts the global loading provider', async () => {
    const router = createMockRouter()

    await router.push('/')
    await router.isReady()

    const wrapper = mount(App, {
      global: {
        plugins: [router],
      },
    })

    expect(wrapper.findComponent(NLoadingBarProvider).exists()).toBe(true)
    expect(wrapper.findComponent(RouterLoadingBar).exists()).toBe(true)

    wrapper.unmount()
  })

  it('navigates to the asynchronous mock route', async () => {
    const router = createMockRouter()

    await router.push('/')
    await router.isReady()

    const wrapper = mount(App, {
      global: {
        plugins: [router],
      },
    })

    const navigation = router.push('/mock')
    await nextTick()
    await nextTick()

    expect(document.body.querySelector('.n-loading-bar-container')).not.toBeNull()

    await navigation
    await flushPromises()
    await nextTick()

    expect(wrapper.get('[data-testid="mock-route"]').text()).toBe('Mock route content')

    wrapper.unmount()
  })
})
