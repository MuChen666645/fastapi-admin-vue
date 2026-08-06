import { describe, expect, it } from 'vitest'

import { hasPermission } from '../utils/permissions'

describe('hasPermission', () => {
  it('matches an explicit permission', () => {
    expect(hasPermission(['system:message:add'], 'system:message:add')).toBe(true)
    expect(hasPermission(['system:message:list'], 'system:message:add')).toBe(false)
  })

  it('matches every permission for a super administrator', () => {
    expect(hasPermission(['*:*:*'], 'system:message:add')).toBe(true)
  })
})
