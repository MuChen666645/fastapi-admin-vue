import { describe, expect, it } from 'vitest'

import { isSafeExternalLink, isSafeRouteName, isSafeRoutePath, isUserRouteMenuType } from '../utils'

describe('路由校验工具', () => {
  it('校验安全的路由路径和名称', () => {
    expect(isSafeRoutePath('system/users')).toBe(true)
    expect(isSafeRoutePath('')).toBe(false)
    expect(isSafeRoutePath('../admin')).toBe(false)
    expect(isSafeRoutePath('system//users')).toBe(false)
    expect(isSafeRoutePath('system/users?tab=roles')).toBe(false)

    expect(isSafeRouteName('用户管理_1')).toBe(true)
    expect(isSafeRouteName('-invalid')).toBe(false)
  })

  it('只接受支持的菜单类型', () => {
    expect(['C', 'L', 'I', 'W'].every(isUserRouteMenuType)).toBe(true)
    expect(isUserRouteMenuType('X')).toBe(false)
  })

  it('只允许不带凭据的 HTTP 外链', () => {
    expect(isSafeExternalLink('https://example.com/docs')).toBe(true)
    expect(isSafeExternalLink('http://example.com')).toBe(true)
    expect(isSafeExternalLink('javascript:alert(1)')).toBe(false)
    expect(isSafeExternalLink('https://user:password@example.com')).toBe(false)
  })
})
