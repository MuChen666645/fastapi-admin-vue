import { describe, expect, it, vi } from 'vitest'

import { flushPromises, mount } from '@vue/test-utils'
import { defineComponent } from 'vue'
import { createMemoryHistory, createRouter } from 'vue-router'

import AppBreadcrumb from '../components/AppBreadcrumb/index.vue'

const RoutePage = defineComponent({
  template: '<div />',
})

const createBreadcrumbRouter = () =>
  createRouter({
    history: createMemoryHistory(),
    routes: [
      {
        path: '/system',
        name: 'system',
        component: RoutePage,
        meta: { title: '系统管理' },
        children: [
          {
            path: 'users',
            name: 'users',
            component: RoutePage,
            meta: { title: '用户管理' },
          },
        ],
      },
    ],
  })

describe('AppBreadcrumb', () => {
  it('handles parent breadcrumb navigation explicitly', async () => {
    const router = createBreadcrumbRouter()
    await router.push('/system/users')
    await router.isReady()

    const wrapper = mount(AppBreadcrumb, {
      global: {
        plugins: [router],
      },
    })

    await flushPromises()
    const parentLink = wrapper.get('.breadcrumb-link')
    expect(parentLink.text()).toBe('系统管理')

    await parentLink.trigger('click')
    await router.isReady()
    await flushPromises()

    expect(router.currentRoute.value.name).toBe('system')
    wrapper.unmount()
  })

  it('opens a validated external menu link without router navigation', async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        {
          path: '/external',
          name: 'external',
          component: RoutePage,
          meta: {
            title: '外链管理',
            menuType: 'L',
            link: 'https://example.com/docs',
          },
          children: [
            {
              path: 'current',
              name: 'external-current',
              component: RoutePage,
              meta: { title: '当前页面' },
            },
          ],
        },
      ],
    })
    await router.push('/external/current')
    await router.isReady()

    const openSpy = vi.spyOn(window, 'open').mockImplementation(() => null)
    const wrapper = mount(AppBreadcrumb, {
      global: {
        plugins: [router],
      },
    })

    await flushPromises()
    await wrapper.get('.breadcrumb-link').trigger('click')

    expect(openSpy).toHaveBeenCalledWith(
      'https://example.com/docs',
      '_blank',
      'noopener,noreferrer',
    )
    expect(router.currentRoute.value.name).toBe('external-current')

    openSpy.mockRestore()
    wrapper.unmount()
  })
})
