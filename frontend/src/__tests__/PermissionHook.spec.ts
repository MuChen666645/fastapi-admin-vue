import { createPinia, setActivePinia } from 'pinia'
import { beforeEach, describe, expect, it } from 'vitest'

import { usePermission } from '@/hooks'
import { useAuthStore } from '@/stores'

describe('usePermission', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('checks explicit, any, and all permissions', () => {
    const auth = useAuthStore()
    auth.permissions = ['system:message:list', 'system:message:add']
    const { hasPermission, hasAnyPermission, hasAllPermissions } = usePermission()

    expect(hasPermission('system:message:list')).toBe(true)
    expect(hasPermission('system:message:edit')).toBe(false)
    expect(hasAnyPermission(['system:message:edit', 'system:message:add'])).toBe(true)
    expect(hasAllPermissions(['system:message:list', 'system:message:add'])).toBe(true)
    expect(hasAllPermissions(['system:message:list', 'system:message:edit'])).toBe(false)
  })

  it('allows every permission for a super administrator', () => {
    const auth = useAuthStore()
    auth.permissions = ['*:*:*']
    const { hasPermission, hasAnyPermission, hasAllPermissions } = usePermission()

    expect(hasPermission('system:message:edit')).toBe(true)
    expect(hasAnyPermission(['system:message:edit'])).toBe(true)
    expect(hasAllPermissions(['system:message:add', 'system:message:remove'])).toBe(true)
  })
})
