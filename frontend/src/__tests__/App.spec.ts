import { describe, it, expect } from 'vitest'

import { mount } from '@vue/test-utils'
import { NLoadingBarProvider } from 'naive-ui'
import { createMemoryHistory, createRouter } from 'vue-router'

import App from '../App.vue'
import RouterLoadingBar from '../components/RouterLoadingBar.vue'

describe('App', () => {
  it('mounts the global loading provider', async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [{ path: '/', component: { template: '<div />' } }],
    })

    await router.push('/')
    await router.isReady()

    const wrapper = mount(App, {
      global: {
        plugins: [router],
      },
    })

    expect(wrapper.findComponent(NLoadingBarProvider).exists()).toBe(true)
    expect(wrapper.findComponent(RouterLoadingBar).exists()).toBe(true)
  })
})
