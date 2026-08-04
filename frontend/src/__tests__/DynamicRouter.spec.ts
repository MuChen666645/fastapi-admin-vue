import { describe, expect, it, vi } from 'vitest'

vi.mock('@/layouts/BasicLayout/index.vue', () => ({ default: {} }))
vi.mock('@/views/error/403.vue', () => ({ default: {} }))
vi.mock('@/views/error/404.vue', () => ({ default: {} }))
vi.mock('@/views/error/500.vue', () => ({ default: {} }))
vi.mock('@/views/error/offline.vue', () => ({ default: {} }))
vi.mock('@/views/change-password/index.vue', () => ({ default: {} }))
vi.mock('@/views/login/index.vue', () => ({ default: {} }))
vi.mock('@/views/demo/form/index.vue', () => ({ default: {} }))

import { buildDynamicRoutes, resolveRouteComponent } from '../router/route-utils'
import { errorRoutes, protectedRoutes, publicRoutes } from '../router/modules'
import { parseUserRoutes } from '../api/user/parsers'

describe('dynamic routes', () => {
  it('uses readable Chinese titles for static routes', () => {
    const routes = [...publicRoutes, ...protectedRoutes, ...errorRoutes]

    expect(routes.map((route) => route.meta?.title)).toEqual([
      '登录',
      '修改密码',
      '管理后台',
      '无权限访问',
      '服务异常',
      '网络离线',
      '页面不存在',
    ])
  })

  it('keeps system settings available as a static authenticated child route', () => {
    const appRoute = protectedRoutes.find((route) => route.name === 'app')
    const settingsRoute = appRoute?.children?.find((route) => route.name === 'system-settings')

    expect(settingsRoute?.path).toBe('system/settings')
    expect(settingsRoute?.meta?.requiresAuth).toBe(true)
    expect(settingsRoute?.meta?.menu).toBe(false)
  })

  it('registers the default pages demo as a nested static menu tree', () => {
    const appRoute = protectedRoutes.find((route) => route.name === 'app')
    const demoRoute = appRoute?.children?.find((route) => route.name === 'demo')
    const defaultPagesRoute = demoRoute?.children?.find((route) => route.name === 'default-pages')
    const leafNames = defaultPagesRoute?.children?.map((route) => route.name)

    expect(demoRoute?.path).toBe('demo')
    expect(demoRoute?.meta?.title).toBe('演示')
    expect(demoRoute?.meta?.requiresAuth).toBe(true)
    expect(demoRoute?.meta?.menu).toBe(true)
    expect(demoRoute?.redirect).toEqual({ name: 'default-pages' })
    expect(defaultPagesRoute?.path).toBe('default-pages')
    expect(defaultPagesRoute?.meta?.title).toBe('缺省页')
    expect(defaultPagesRoute?.meta?.requiresAuth).toBe(true)
    expect(defaultPagesRoute?.meta?.menu).toBe(true)
    expect(defaultPagesRoute?.redirect).toEqual({ name: 'default-page-forbidden' })
    expect(leafNames).toEqual([
      'default-page-forbidden',
      'default-page-not-found',
      'default-page-server-error',
      'default-page-offline',
    ])
  })

  it('registers the form component demo under the features menu', () => {
    const appRoute = protectedRoutes.find((route) => route.name === 'app')
    const demoRoute = appRoute?.children?.find((route) => route.name === 'demo')
    const featuresRoute = demoRoute?.children?.find((route) => route.name === 'demo-features')
    const formRoute = featuresRoute?.children?.find((route) => route.name === 'demo-form')

    expect(featuresRoute?.path).toBe('features')
    expect(featuresRoute?.meta?.title).toBe('功能')
    expect(featuresRoute?.meta?.requiresAuth).toBe(true)
    expect(featuresRoute?.meta?.menu).toBe(true)
    expect(featuresRoute?.redirect).toEqual({ name: 'demo-form' })
    expect(formRoute?.path).toBe('form')
    expect(formRoute?.meta?.title).toBe('表单')
    expect(formRoute?.meta?.requiresAuth).toBe(true)
    expect(formRoute?.meta?.menu).toBe(true)
  })

  it('filters unknown backend components and warns once', () => {
    const warnSpy = vi.spyOn(console, 'warn').mockImplementation(() => undefined)

    try {
      const routes = parseUserRoutes([
        {
          path: 'dashboard',
          name: 'dashboard',
          component: 'home/index',
          redirect: null,
          hidden: false,
          meta: { title: '首页', icon: null, noCache: false, link: null },
          children: [],
        },
        {
          path: 'unknown',
          name: 'unknown',
          component: 'server/execute',
          redirect: null,
          hidden: false,
          meta: { title: '未知页面', icon: null, noCache: true, link: null },
          children: [],
        },
        {
          path: 'docs',
          name: 'docs',
          component: null,
          redirect: null,
          hidden: false,
          meta: {
            title: '在线文档',
            menuType: 'L',
            icon: null,
            noCache: true,
            link: 'https://example.com/docs',
          },
          children: [],
        },
      ])

      expect(buildDynamicRoutes(routes).map((route) => route.name)).toEqual(['dashboard', 'docs'])
      expect(warnSpy).toHaveBeenCalledTimes(1)
      expect(warnSpy).toHaveBeenCalledWith(expect.stringContaining('server/execute'))
    } finally {
      warnSpy.mockRestore()
    }
  })

  it('normalizes frontend view paths before resolving local components', () => {
    const directComponent = resolveRouteComponent('home/index.vue')
    const aliasComponent = resolveRouteComponent('@/views/home/index.vue')
    const relativeComponent = resolveRouteComponent('../views/home/index.vue')
    const relativeViewComponent = resolveRouteComponent('./views/home/index.vue')
    const rootViewComponent = resolveRouteComponent('/views/home/index.vue')

    expect(directComponent).not.toBeNull()
    expect(typeof directComponent).toBe('function')
    expect(Object.prototype.hasOwnProperty.call(directComponent, '__asyncLoader')).toBe(false)
    expect(aliasComponent).toBe(directComponent)
    expect(relativeComponent).toBe(directComponent)
    expect(relativeViewComponent).toBe(directComponent)
    expect(rootViewComponent).toBe(directComponent)
  })

  it('rejects unsafe backend route paths before registration', () => {
    expect(
      parseUserRoutes([
        {
          path: '../admin',
          name: 'unsafe',
          component: 'home/index',
          redirect: null,
          hidden: false,
          meta: { title: '危险路由', icon: null, noCache: true, link: null },
          children: [],
        },
      ]),
    ).toEqual([])
  })

  it('redirects container menus to their first navigable child', () => {
    const routes = parseUserRoutes([
      {
        path: 'system',
        name: 'system',
        component: null,
        redirect: null,
        hidden: false,
        meta: { title: '系统管理', menuType: 'C', icon: null, noCache: true, link: null },
        children: [
          {
            path: 'users',
            name: 'users',
            component: 'home/index',
            redirect: null,
            hidden: false,
            meta: { title: '用户管理', menuType: 'C', icon: null, noCache: true, link: null },
            children: [],
          },
        ],
      },
    ])

    const systemRoute = buildDynamicRoutes(routes).find((route) => route.name === 'system')
    expect(systemRoute?.redirect).toEqual({ name: 'users' })
  })
})
