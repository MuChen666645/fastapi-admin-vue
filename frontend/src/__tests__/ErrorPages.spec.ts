import { describe, expect, it } from 'vitest'

import { flushPromises, mount } from '@vue/test-utils'
import { createPinia } from 'pinia'
import { createRouter, createMemoryHistory } from 'vue-router'

import ErrorStatePage from '../views/error/components/ErrorStatePage.vue'

describe('error state page', () => {
  it('renders the status actions and returns to the application home', async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/', name: 'app', component: { template: '<div />' } },
        { path: '/500', name: 'server-error', component: { template: '<div />' } },
      ],
    })
    await router.push('/500')
    await router.isReady()

    const wrapper = mount(ErrorStatePage, {
      props: {
        code: '500',
        titleKey: 'error.server.title',
        descriptionKey: 'error.server.description',
        animationData: {},
      },
      global: {
        plugins: [router, createPinia()],
      },
    })

    expect(wrapper.get('.error-code').text()).toBe('500')
    expect(wrapper.findAll('button')).toHaveLength(2)
    expect(wrapper.text()).toContain('服务暂时不可用')

    await wrapper.findAll('button')[1]?.trigger('click')
    await flushPromises()
    expect(router.currentRoute.value.name).toBe('app')

    wrapper.unmount()
  })
})
