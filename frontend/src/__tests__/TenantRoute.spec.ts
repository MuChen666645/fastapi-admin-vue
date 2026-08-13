import { describe, expect, it } from 'vitest'

import { buildDynamicRoutes } from '@/router/route-utils'
import { parseUserRoutes } from '@/api/user/parsers'

describe('Tenant route', () => {
  it('resolves the backend tenant menu to the local platform tenant page', () => {
    const routes = parseUserRoutes([
      {
        path: 'system/tenant',
        name: 'system-tenant',
        component: 'system/tenant/index',
        redirect: null,
        hidden: false,
        meta: { title: '租户管理', icon: 'BusinessOutline', noCache: false, link: null },
        children: [],
      },
    ])

    expect(buildDynamicRoutes(routes).map((route) => route.name)).toEqual(['system-tenant'])
  })
})
