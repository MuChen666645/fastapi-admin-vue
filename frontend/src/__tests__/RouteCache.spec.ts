import { defineComponent, h, KeepAlive, nextTick, ref } from 'vue'
import { flushPromises, mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter, RouterView } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'
import { describe, expect, it } from 'vitest'

import { useRouteCache } from '../hooks/useRouteCache'
import { getRouteCacheName } from '../router/route-cache'
import { useTabsStore } from '../stores'
import type { RouteViewSlot } from '../types'

const createCounterView = (testId: string) =>
  defineComponent({
    setup: () => {
      const count = ref(0)
      return () =>
        h(
          'button',
          { 'data-test': testId, type: 'button', onClick: () => (count.value += 1) },
          String(count.value),
        )
    },
  })

const createRouteCacheHost = () =>
  defineComponent({
    setup: () => {
      const { cachedComponentNames, getCachedRouteComponent, getRouteKey } = useRouteCache()

      return () =>
        h(
          RouterView,
          {},
          {
            default: ({ Component, route }: RouteViewSlot) => {
              if (!Component) {
                return h('div')
              }

              const cachedComponent = getCachedRouteComponent(Component, route)
              if (!cachedComponent) {
                return h('div')
              }

              return h(KeepAlive, { include: cachedComponentNames.value }, () =>
                h(cachedComponent, { key: getRouteKey(route) }),
              )
            },
          },
        )
    },
  })

const createTestRouter = () => {
  const cachedView = createCounterView('cached')
  const nonCachedView = createCounterView('non-cached')

  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/cached', name: 'cached', component: cachedView, meta: { noCache: false } },
      {
        path: '/non-cached',
        name: 'non-cached',
        component: nonCachedView,
        meta: { noCache: true },
      },
      { path: '/other', name: 'other', component: { render: () => h('div', 'other') } },
    ],
  })
}

const createNestedTestRouter = () => {
  const roleView = createCounterView('nested-role')
  const userView = createCounterView('nested-user')

  return createRouter({
    history: createMemoryHistory(),
    routes: [
      {
        path: '/system',
        component: RouterView,
        children: [
          { path: 'role', name: 'nested-role', component: roleView, meta: { noCache: false } },
          { path: 'user', name: 'nested-user', component: userView, meta: { noCache: false } },
        ],
      },
    ],
  })
}

describe('route component cache', () => {
  it('preserves cached route state and recreates non-cached route state', async () => {
    setActivePinia(createPinia())
    const router = createTestRouter()
    const tabsStore = useTabsStore()
    tabsStore.addTab({
      key: 'cached',
      title: 'Cached',
      fullPath: '/cached',
      icon: null,
      cacheName: getRouteCacheName('cached'),
      cacheable: true,
      closable: false,
    })
    await router.push('/cached')
    await router.isReady()

    const wrapper = mount(createRouteCacheHost(), {
      global: { plugins: [router] },
    })

    await nextTick()
    await wrapper.get('[data-test="cached"]').trigger('click')
    await router.push('/other')
    await router.push('/cached')
    await nextTick()
    expect(wrapper.get('[data-test="cached"]').text()).toBe('1')

    await router.push('/non-cached')
    await nextTick()
    await wrapper.get('[data-test="non-cached"]').trigger('click')
    await router.push('/other')
    await router.push('/non-cached')
    await nextTick()
    expect(wrapper.get('[data-test="non-cached"]').text()).toBe('0')

    wrapper.unmount()
  })

  it('keeps cached nested router views bound to their original route', async () => {
    setActivePinia(createPinia())
    const router = createNestedTestRouter()
    const tabsStore = useTabsStore()
    const runtimeErrors: unknown[] = []
    tabsStore.addTab({
      key: 'nested-role',
      title: 'Role',
      fullPath: '/system/role',
      icon: null,
      cacheName: getRouteCacheName('nested-role'),
      cacheable: true,
      closable: false,
    })
    tabsStore.addTab({
      key: 'nested-user',
      title: 'User',
      fullPath: '/system/user',
      icon: null,
      cacheName: getRouteCacheName('nested-user'),
      cacheable: true,
      closable: true,
    })

    await router.push('/system/role')
    await router.isReady()

    const wrapper = mount(createRouteCacheHost(), {
      global: {
        plugins: [router],
        config: {
          errorHandler: (error) => runtimeErrors.push(error),
        },
      },
    })

    await nextTick()
    await wrapper.get('[data-test="nested-role"]').trigger('click')
    expect(wrapper.get('[data-test="nested-role"]').text()).toBe('1')
    await router.push('/system/user')
    await flushPromises()
    await nextTick()
    expect(wrapper.get('[data-test="nested-user"]').text()).toBe('0')

    await router.push('/system/role')
    await flushPromises()
    await nextTick()
    expect(wrapper.get('[data-test="nested-role"]').text()).toBe('1')
    expect(runtimeErrors).toEqual([])

    wrapper.unmount()
  })
})
