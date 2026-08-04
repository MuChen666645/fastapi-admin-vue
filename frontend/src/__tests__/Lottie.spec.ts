import { describe, expect, it, vi } from 'vitest'

import { flushPromises, mount } from '@vue/test-utils'
import { defineComponent, nextTick } from 'vue'
import { createPinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'

const lottieMock = vi.hoisted(() => ({
  loadAnimation: vi.fn(),
}))

const animationMock = vi.hoisted(() => ({
  destroy: vi.fn(),
  pause: vi.fn(),
  play: vi.fn(),
}))

vi.mock('lottie-web', () => ({ default: lottieMock }))

import GlobalLoading from '../components/GlobalLoading/index.vue'
import ContentLoading from '../components/ContentLoading/index.vue'
import {
  destroyLottieAnimation,
  loadLottieAnimation,
  pauseLottieAnimation,
  playLottieAnimation,
} from '../utils/lottie'
import { getRouteCacheName } from '../router/route-cache'
import { useTabsStore } from '../stores'
import { useRouteLoadingStore } from '../stores/modules/route-loading'

const RoutePage = defineComponent({ template: '<div>route</div>' })

describe('lottie utilities', () => {
  it('loads an animation with the configured renderer and playback options', () => {
    lottieMock.loadAnimation.mockReturnValue(animationMock)
    const container = document.createElement('div')
    const animationData = { v: '5.9.4' }

    const animation = loadLottieAnimation(container, animationData, {
      autoplay: false,
      loop: 2,
      renderer: 'canvas',
    })

    expect(animation).toBe(animationMock)
    expect(lottieMock.loadAnimation).toHaveBeenCalledWith({
      animationData,
      autoplay: false,
      container,
      loop: 2,
      renderer: 'canvas',
    })
  })

  it('guards playback and destruction calls for missing animations', () => {
    expect(() => playLottieAnimation(null)).not.toThrow()
    expect(() => pauseLottieAnimation(null)).not.toThrow()
    expect(() => destroyLottieAnimation(null)).not.toThrow()

    playLottieAnimation(animationMock)
    pauseLottieAnimation(animationMock)
    destroyLottieAnimation(animationMock)

    expect(animationMock.play).toHaveBeenCalledOnce()
    expect(animationMock.pause).toHaveBeenCalledOnce()
    expect(animationMock.destroy).toHaveBeenCalledOnce()
  })
})

describe('GlobalLoading', () => {
  it('shows for non-cached routes and skips cached route navigation', async () => {
    vi.useFakeTimers()

    try {
      lottieMock.loadAnimation.mockReturnValue(animationMock)
      const pinia = createPinia()
      const tabsStore = useTabsStore(pinia)
      tabsStore.addTab({
        key: 'cached',
        title: '缓存页面',
        fullPath: '/cached',
        icon: null,
        cacheName: getRouteCacheName('cached'),
        cacheable: true,
        closable: true,
      })
      let resolveNavigation: (() => void) | undefined
      const navigationGate = new Promise<void>((resolve) => {
        resolveNavigation = resolve
      })
      const router = createRouter({
        history: createMemoryHistory(),
        routes: [
          {
            path: '/cached',
            name: 'cached',
            component: RoutePage,
            meta: { noCache: false },
          },
          {
            path: '/non-cached',
            name: 'non-cached',
            component: RoutePage,
            meta: { noCache: true },
            beforeEnter: async () => {
              await navigationGate
            },
          },
        ],
      })
      await router.push('/cached')
      await router.isReady()

      const wrapper = mount(GlobalLoading, {
        global: {
          plugins: [pinia, router],
        },
      })

      await flushPromises()
      await vi.advanceTimersByTimeAsync(300)
      expect(wrapper.get('[data-testid="global-loading"]').attributes('aria-hidden')).toBe('true')

      const navigation = router.push('/non-cached')
      await flushPromises()
      expect(wrapper.get('[data-testid="global-loading"]').attributes('aria-hidden')).toBe('false')
      expect(animationMock.play).toHaveBeenCalled()

      resolveNavigation?.()
      await navigation
      await flushPromises()
      await vi.advanceTimersByTimeAsync(300)

      expect(wrapper.get('[data-testid="global-loading"]').attributes('aria-hidden')).toBe('true')
      expect(animationMock.pause).toHaveBeenCalled()

      await router.push('/cached')
      expect(wrapper.get('[data-testid="global-loading"]').attributes('aria-hidden')).toBe('true')

      wrapper.unmount()
      expect(animationMock.destroy).toHaveBeenCalled()
    } finally {
      vi.useRealTimers()
    }
  })

  it('keeps loading active when a pending navigation is cancelled by a newer one', async () => {
    vi.useFakeTimers()

    try {
      lottieMock.loadAnimation.mockReturnValue(animationMock)
      const pinia = createPinia()
      let resolveSlowNavigation: (() => void) | undefined
      let resolveFastNavigation: (() => void) | undefined
      const slowNavigationGate = new Promise<void>((resolve) => {
        resolveSlowNavigation = resolve
      })
      const fastNavigationGate = new Promise<void>((resolve) => {
        resolveFastNavigation = resolve
      })
      const router = createRouter({
        history: createMemoryHistory(),
        routes: [
          {
            path: '/home',
            name: 'home',
            component: RoutePage,
            meta: { noCache: true },
          },
          {
            path: '/slow',
            name: 'slow',
            component: RoutePage,
            meta: { noCache: true },
            beforeEnter: async () => {
              await slowNavigationGate
            },
          },
          {
            path: '/fast',
            name: 'fast',
            component: RoutePage,
            meta: { noCache: true },
            beforeEnter: async () => {
              await fastNavigationGate
            },
          },
        ],
      })

      await router.push('/home')
      await router.isReady()

      const wrapper = mount(GlobalLoading, {
        global: {
          plugins: [pinia, router],
        },
      })
      const routeLoading = useRouteLoadingStore(pinia)

      await flushPromises()
      await vi.advanceTimersByTimeAsync(300)

      const slowNavigation = router.push('/slow')
      await flushPromises()
      const fastNavigation = router.push('/fast')
      resolveSlowNavigation?.()
      await flushPromises()
      await vi.advanceTimersByTimeAsync(300)

      expect(routeLoading.visible).toBe(true)
      expect(wrapper.get('[data-testid="global-loading"]').attributes('aria-hidden')).toBe('false')

      resolveFastNavigation?.()
      await Promise.all([slowNavigation, fastNavigation])
      await flushPromises()
      await vi.advanceTimersByTimeAsync(300)

      expect(routeLoading.visible).toBe(false)
      expect(wrapper.get('[data-testid="global-loading"]').attributes('aria-hidden')).toBe('true')

      wrapper.unmount()
    } finally {
      vi.useRealTimers()
    }
  })

  it('renders content loading only for layout content scope', async () => {
    const pinia = createPinia()
    const routeLoading = useRouteLoadingStore(pinia)
    routeLoading.start('content')

    const wrapper = mount(ContentLoading, {
      global: {
        plugins: [pinia],
      },
    })

    await nextTick()
    expect(wrapper.get('[data-testid="content-loading"]').attributes('aria-hidden')).toBe('false')

    routeLoading.setScope('screen')
    await nextTick()
    expect(wrapper.get('[data-testid="content-loading"]').attributes('aria-hidden')).toBe('true')

    wrapper.unmount()
  })

  it('keeps screen loading for routes outside the application layout', async () => {
    vi.useFakeTimers()

    try {
      lottieMock.loadAnimation.mockReturnValue(animationMock)
      const pinia = createPinia()
      const router = createRouter({
        history: createMemoryHistory(),
        routes: [
          {
            path: '/login',
            name: 'login',
            component: RoutePage,
          },
          {
            path: '/',
            name: 'app',
            component: defineComponent({ template: '<router-view />' }),
            children: [
              {
                path: 'home',
                name: 'home',
                component: RoutePage,
                meta: { noCache: true },
              },
              {
                path: 'settings',
                name: 'settings',
                component: RoutePage,
                meta: { noCache: true },
              },
            ],
          },
        ],
      })

      await router.push('/login')
      await router.isReady()

      const globalWrapper = mount(GlobalLoading, {
        global: {
          plugins: [pinia, router],
        },
      })
      const contentWrapper = mount(ContentLoading, {
        global: {
          plugins: [pinia],
        },
      })

      await flushPromises()
      await vi.advanceTimersByTimeAsync(300)

      await router.push('/home')
      await nextTick()
      expect(globalWrapper.get('[data-testid="global-loading"]').attributes('aria-hidden')).toBe(
        'true',
      )
      expect(contentWrapper.get('[data-testid="content-loading"]').attributes('aria-hidden')).toBe(
        'false',
      )

      await vi.advanceTimersByTimeAsync(300)
      await router.push('/login')
      await nextTick()
      expect(globalWrapper.get('[data-testid="global-loading"]').attributes('aria-hidden')).toBe(
        'false',
      )
      expect(contentWrapper.get('[data-testid="content-loading"]').attributes('aria-hidden')).toBe(
        'true',
      )

      globalWrapper.unmount()
      contentWrapper.unmount()
    } finally {
      vi.useRealTimers()
    }
  })
})
