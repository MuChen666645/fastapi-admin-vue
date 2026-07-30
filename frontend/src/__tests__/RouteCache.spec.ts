import { defineComponent, h, KeepAlive, nextTick, ref } from 'vue'
import { mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter, RouterView } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'
import { describe, expect, it } from 'vitest'

import { useRouteCache } from '../hooks/useRouteCache'
import { getRouteCacheName } from '../router/route-cache'
import { useTabsStore } from '../stores'

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
            default: ({ Component, route }) =>
              h(KeepAlive, { include: cachedComponentNames.value }, () =>
                h(getCachedRouteComponent(Component, route), {
                  key: getRouteKey(route),
                }),
              ),
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
})
