import { describe, expect, it, vi } from 'vitest'
import { createMemoryHistory, createRouter } from 'vue-router'

const authStore = vi.hoisted(() => ({
  useAuthStore: vi.fn(),
}))
const findFirstVisibleRouteName = vi.hoisted(() => vi.fn())

vi.mock('@/stores', () => authStore)
vi.mock('../router/route-utils', () => ({ findFirstVisibleRouteName }))

import { createAuthGuard } from '../router/guards/auth'

const createTestRouter = () =>
  createRouter({
    history: createMemoryHistory(),
    routes: [
      {
        path: '/login',
        name: 'login',
        component: { render: () => null },
        meta: { public: true },
      },
      {
        path: '/:pathMatch(.*)*',
        name: 'not-found',
        component: { render: () => null },
        meta: { public: true },
      },
    ],
  })

describe('认证路由守卫', () => {
  it('未认证访问未知地址时跳转登录页而不是放行到 404', async () => {
    const router = createTestRouter()
    await router.push('/login')
    await router.isReady()
    const from = router.currentRoute.value

    const auth = {
      accessToken: null,
      hasSession: false,
      status: 'signed-out',
      initializeSession: vi.fn().mockResolvedValue(false),
    }
    authStore.useAuthStore.mockReturnValue(auth)

    const guard = createAuthGuard(router, vi.fn())
    await router.push('/missing-page')
    const result = await guard(router.currentRoute.value, from, vi.fn())

    expect(result).toEqual({
      name: 'login',
      query: { redirect: '/missing-page' },
    })
  })

  it('认证初始化失败时将失效会话带回登录页', async () => {
    const router = createTestRouter()
    await router.push('/login')
    await router.isReady()
    const from = router.currentRoute.value
    const auth = {
      accessToken: 'expired-access-token',
      hasSession: true,
      status: 'initializing',
      initializeSession: vi.fn().mockResolvedValue(false),
    }
    authStore.useAuthStore.mockReturnValue(auth)

    const guard = createAuthGuard(router, vi.fn())
    await router.push('/missing-page')
    const result = await guard(router.currentRoute.value, from, vi.fn())

    expect(result).toEqual({
      name: 'login',
      query: { redirect: '/missing-page' },
    })
  })
})
