import { describe, expect, it, vi } from 'vitest'

vi.mock('@/layouts/BasicLayout/index.vue', () => ({ default: {} }))
vi.mock('@/views/error/403.vue', () => ({ default: {} }))
vi.mock('@/views/error/404.vue', () => ({ default: {} }))
vi.mock('@/views/change-password/index.vue', () => ({ default: {} }))
vi.mock('@/views/login/index.vue', () => ({ default: {} }))

import { buildDynamicRoutes } from '../router/route-utils'
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
      '页面不存在',
    ])
  })

  it('keeps known local components and isolates unknown backend components', () => {
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
