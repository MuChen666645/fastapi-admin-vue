import { describe, expect, it } from 'vitest'

import {
  createTenantMemberAddPayload,
  createTenantPayload,
  createTenantUpdatePayload,
} from '@/views/system/tenant/payloads'

describe('Tenant payloads', () => {
  it('trims optional tenant fields and preserves the optimistic-lock version', () => {
    expect(
      createTenantPayload({
        code: ' tenant-a ',
        name: ' Tenant A ',
        description: ' ',
        status: '1',
      }),
    ).toEqual({ code: 'tenant-a', name: 'Tenant A', description: null })

    expect(
      createTenantUpdatePayload(
        { code: 'tenant-a', name: ' Tenant A ', description: ' Updated ', status: '0' },
        3,
      ),
    ).toEqual({ name: 'Tenant A', description: 'Updated', status: '0', version: 3 })
  })

  it('only creates member payloads for positive integer user IDs', () => {
    expect(createTenantMemberAddPayload({ user_id: null, is_default: false })).toBeNull()
    expect(createTenantMemberAddPayload({ user_id: 0, is_default: false })).toBeNull()
    expect(createTenantMemberAddPayload({ user_id: 8.5, is_default: false })).toBeNull()
    expect(createTenantMemberAddPayload({ user_id: 8, is_default: true })).toEqual({
      user_id: 8,
      is_default: true,
    })
  })
})
