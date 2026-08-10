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
      {
        path: '/403',
        name: 'forbidden',
        component: { render: () => null },
        meta: { requiresAuth: true },
      },
      {
        path: '/system/dict/data',
        name: 'system-dict-data',
        component: { render: () => null },
        meta: {
          requiresAuth: true,
          permission: ['system:dict:list', 'system:dict:query'],
        },
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

  it('拒绝缺少路由权限的静态页面访问', async () => {
    const router = createTestRouter()
    await router.push('/login')
    await router.isReady()
    const from = router.currentRoute.value
    const auth = {
      accessToken: 'access-token',
      hasSession: true,
      status: 'authenticated',
      permissions: ['system:dict:list'],
      routes: [],
      initializeSession: vi.fn().mockResolvedValue(true),
    }
    authStore.useAuthStore.mockReturnValue(auth)

    const guard = createAuthGuard(router, vi.fn())
    await router.push('/system/dict/data')
    const result = await guard(router.currentRoute.value, from, vi.fn())

    expect(result).toEqual({ name: 'forbidden' })
  })

  it('允许拥有路由权限的静态页面访问', async () => {
    const router = createTestRouter()
    await router.push('/login')
    await router.isReady()
    const from = router.currentRoute.value
    const auth = {
      accessToken: 'access-token',
      hasSession: true,
      status: 'authenticated',
      permissions: ['system:dict:list', 'system:dict:query'],
      routes: [],
      initializeSession: vi.fn().mockResolvedValue(true),
    }
    authStore.useAuthStore.mockReturnValue(auth)
    const registerRoutes = vi.fn()

    const guard = createAuthGuard(router, registerRoutes)
    await router.push('/system/dict/data')
    const result = await guard(router.currentRoute.value, from, vi.fn())

    expect(result).toBe(true)
    expect(registerRoutes).toHaveBeenCalledWith([])
  })

  it('拒绝格式非法的路由权限元数据', async () => {
    const router = createTestRouter()
    const routeRecord = router.getRoutes().find((route) => route.name === 'system-dict-data')
    if (!routeRecord) {
      throw new Error('缺少字典数据测试路由')
    }

    Reflect.set(routeRecord.meta, 'permission', ['system:dict:list', 1])
    await router.push('/login')
    await router.isReady()
    const from = router.currentRoute.value
    const auth = {
      accessToken: 'access-token',
      hasSession: true,
      status: 'authenticated',
      permissions: ['*:*:*'],
      routes: [],
      initializeSession: vi.fn().mockResolvedValue(true),
    }
    authStore.useAuthStore.mockReturnValue(auth)

    const guard = createAuthGuard(router, vi.fn())
    await router.push('/system/dict/data')
    const result = await guard(router.currentRoute.value, from, vi.fn())

    expect(result).toEqual({ name: 'forbidden' })
  })

  it('通过真实路由导航拒绝缺少权限的静态页面', async () => {
    const router = createTestRouter()
    router.beforeEach(createAuthGuard(router, vi.fn()))
    const auth = {
      accessToken: 'access-token',
      hasSession: true,
      status: 'authenticated',
      permissions: ['system:dict:list'],
      routes: [],
      initializeSession: vi.fn().mockResolvedValue(true),
    }
    authStore.useAuthStore.mockReturnValue(auth)

    await router.push('/system/dict/data')

    expect(router.currentRoute.value.name).toBe('forbidden')
  })

  it('通过真实路由导航允许超级权限访问静态页面', async () => {
    const router = createTestRouter()
    router.beforeEach(createAuthGuard(router, vi.fn()))
    const auth = {
      accessToken: 'access-token',
      hasSession: true,
      status: 'authenticated',
      permissions: ['*:*:*'],
      routes: [],
      initializeSession: vi.fn().mockResolvedValue(true),
    }
    authStore.useAuthStore.mockReturnValue(auth)

    await router.push('/system/dict/data')

    expect(router.currentRoute.value.name).toBe('system-dict-data')
  })
})
