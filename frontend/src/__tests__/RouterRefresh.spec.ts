import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { createPinia, setActivePinia } from 'pinia'

import router, { clearAuthenticatedRoutes } from '../router'
import { useAuthStore } from '../stores'
import type { UserRoute } from '../types'

const authorizedRoute: UserRoute = {
  path: 'system/config',
  name: 'config',
  component: 'system/config/index',
  redirect: null,
  hidden: false,
  meta: {
    title: '系统参数',
    menuType: 'C',
    icon: null,
    noCache: false,
    link: null,
  },
  children: [],
}

describe('路由刷新恢复', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    clearAuthenticatedRoutes()

    const auth = useAuthStore()
    auth.applyTokens({
      access_token: 'access-token',
      refresh_token: 'refresh-token',
      token_type: 'bearer',
      expires_in: 3600,
      must_change_password: false,
    })
    auth.routes = [authorizedRoute]
    vi.spyOn(auth, 'initializeSession').mockResolvedValue(true)
  })

  afterEach(() => {
    clearAuthenticatedRoutes()
  })

  it('刷新动态菜单地址时会先注册路由再重新解析', async () => {
    await router.push('/system/config?tab=general')

    expect(router.currentRoute.value.name).toBe('config')
    expect(router.currentRoute.value.query).toEqual({ tab: 'general' })
  })
})
