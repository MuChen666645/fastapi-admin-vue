import { describe, expect, it } from 'vitest'

import { mount } from '@vue/test-utils'
import { NLoadingBarProvider } from 'naive-ui'
import { defineComponent } from 'vue'
import { createMemoryHistory, createRouter } from 'vue-router'

import App from '../App.vue'
import RouterLoadingBar from '../components/RouterLoadingBar/index.vue'

const LoginPage = defineComponent({ template: '<div data-testid="login-page">Login page</div>' })

describe('App', () => {
  it('mounts the global loading provider', async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [{ path: '/', component: LoginPage }],
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

    wrapper.unmount()
  })
})
