import { describe, expect, it } from 'vitest'

import { buildDynamicRoutes } from '../router/dynamic'
import { parseUserRoutes } from '../api/user/parsers'

describe('dynamic routes', () => {
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
    ])

    expect(buildDynamicRoutes(routes).map((route) => route.name)).toEqual(['dashboard'])
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
})
