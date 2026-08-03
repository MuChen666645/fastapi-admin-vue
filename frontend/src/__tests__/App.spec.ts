import { describe, expect, it } from 'vitest'

import { mount } from '@vue/test-utils'
import { NLoadingBarProvider } from 'naive-ui'
import { createPinia } from 'pinia'
import { defineComponent, nextTick } from 'vue'
import { createMemoryHistory, createRouter } from 'vue-router'

import App from '../App.vue'
import GlobalLoading from '../components/GlobalLoading/index.vue'
import RouterLoadingBar from '../components/RouterLoadingBar/index.vue'
import { usePreferencesStore } from '../stores'

const LoginPage = defineComponent({ template: '<div data-testid="login-page">Login page</div>' })

describe('App', () => {
  it('mounts the global loading provider', async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [{ path: '/', component: LoginPage }],
    })

    await router.push('/')
    await router.isReady()

    const pinia = createPinia()
    const wrapper = mount(App, {
      global: {
        plugins: [pinia, router],
      },
    })

    expect(wrapper.findComponent(NLoadingBarProvider).exists()).toBe(true)
    expect(wrapper.findComponent(GlobalLoading).exists()).toBe(true)
    expect(wrapper.findComponent(RouterLoadingBar).exists()).toBe(true)

    const preferences = usePreferencesStore(pinia)
    preferences.accentColor = 'rose'
    await nextTick()

    expect(document.documentElement.style.getPropertyValue('--app-color-primary')).toBe('#e94b78')
    expect(document.documentElement.style.getPropertyValue('--app-color-header-start')).toBe('')
    expect(document.documentElement.style.getPropertyValue('--app-color-sidebar')).toBe('')

    wrapper.unmount()
  })
})
