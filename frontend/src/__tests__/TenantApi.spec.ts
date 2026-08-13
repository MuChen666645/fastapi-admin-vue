import { beforeEach, describe, expect, it, vi } from 'vitest'

const requestJson = vi.hoisted(() => vi.fn())

vi.mock('../utils/request', () => ({ requestJson }))

import {
  addTenantMember,
  createTenant,
  deleteTenant,
  fetchTenantMembers,
  fetchTenants,
  removeTenantMember,
  updateTenant,
  updateTenantMember,
} from '@/api/tenant'

describe('Tenant API', () => {
  beforeEach(() => {
    requestJson.mockReset()
    requestJson.mockResolvedValue(null)
  })

  it('uses only the backend platform tenant contracts', async () => {
    const createPayload = { code: 'tenant-a', name: 'Tenant A', description: null }
    const updatePayload = {
      name: 'Tenant A',
      description: 'Updated',
      status: '1' as const,
      version: 3,
    }
    const memberAddPayload = { user_id: 8, is_default: true }
    const memberUpdatePayload = { status: '0' as const, is_default: false, version: 4 }

    await fetchTenants()
    await createTenant(createPayload)
    await updateTenant(7, updatePayload)
    await deleteTenant(7, 3)
    await fetchTenantMembers(7)
    await addTenantMember(7, memberAddPayload)
    await updateTenantMember(7, 8, memberUpdatePayload)
    await removeTenantMember(7, 8, 4)

    expect(requestJson).toHaveBeenNthCalledWith(1, '/tenant/list/all', {}, expect.any(Function))
    expect(requestJson).toHaveBeenNthCalledWith(
      2,
      '/tenant/add',
      { method: 'POST', data: createPayload },
      expect.any(Function),
    )
    expect(requestJson).toHaveBeenNthCalledWith(
      3,
      '/tenant/7',
      { method: 'PUT', data: updatePayload },
      expect.any(Function),
    )
    expect(requestJson).toHaveBeenNthCalledWith(
      4,
      '/tenant/7',
      { method: 'DELETE', params: { version: 3 } },
      expect.any(Function),
    )
    expect(requestJson).toHaveBeenNthCalledWith(5, '/tenant/7/members', {}, expect.any(Function))
    expect(requestJson).toHaveBeenNthCalledWith(
      6,
      '/tenant/7/members',
      { method: 'POST', data: memberAddPayload },
      expect.any(Function),
    )
    expect(requestJson).toHaveBeenNthCalledWith(
      7,
      '/tenant/7/members/8',
      { method: 'PUT', data: memberUpdatePayload },
      expect.any(Function),
    )
    expect(requestJson).toHaveBeenNthCalledWith(
      8,
      '/tenant/7/members/8',
      { method: 'DELETE', params: { version: 4 } },
      expect.any(Function),
    )
  })

  it('rejects malformed tenant and member records', async () => {
    const { parseTenant, parseTenantMembers } = await import('@/api/tenant/parsers')

    expect(() =>
      parseTenant({
        id: 1,
        code: 'tenant-a',
        name: 'Tenant A',
        description: null,
        status: 'invalid',
        version: 1,
        deleted_at: null,
        create_time: '2026-08-13T09:00:00',
        update_time: '2026-08-13T09:00:00',
      }),
    ).toThrow('接口字段 status 无效')

    expect(() => parseTenantMembers({})).toThrow('租户成员列表响应无效')
  })
})
