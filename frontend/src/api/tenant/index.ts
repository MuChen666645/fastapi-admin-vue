import type {
  Tenant,
  TenantCreatePayload,
  TenantMember,
  TenantMemberAddPayload,
  TenantMemberUpdatePayload,
  TenantUpdatePayload,
} from '@/types'
import { requestJson } from '@/utils/request'

import { parseTenant, parseTenantMemberResult, parseTenantMembers, parseTenants } from './parsers'

export const fetchTenants = (): Promise<Tenant[]> =>
  requestJson('/tenant/list/all', {}, parseTenants)

export const createTenant = (payload: TenantCreatePayload): Promise<Tenant> =>
  requestJson('/tenant/add', { method: 'POST', data: payload }, parseTenant)

export const updateTenant = (tenantId: number, payload: TenantUpdatePayload): Promise<null> =>
  requestJson(`/tenant/${tenantId}`, { method: 'PUT', data: payload }, () => null)

export const deleteTenant = (tenantId: number, version: number): Promise<null> =>
  requestJson(`/tenant/${tenantId}`, { method: 'DELETE', params: { version } }, () => null)

export const fetchTenantMembers = (tenantId: number): Promise<TenantMember[]> =>
  requestJson(`/tenant/${tenantId}/members`, {}, parseTenantMembers)

export const addTenantMember = (
  tenantId: number,
  payload: TenantMemberAddPayload,
): Promise<TenantMember> =>
  requestJson(
    `/tenant/${tenantId}/members`,
    { method: 'POST', data: payload },
    parseTenantMemberResult,
  )

export const updateTenantMember = (
  tenantId: number,
  userId: number,
  payload: TenantMemberUpdatePayload,
): Promise<null> =>
  requestJson(`/tenant/${tenantId}/members/${userId}`, { method: 'PUT', data: payload }, () => null)

export const removeTenantMember = (
  tenantId: number,
  userId: number,
  version: number,
): Promise<null> =>
  requestJson(
    `/tenant/${tenantId}/members/${userId}`,
    { method: 'DELETE', params: { version } },
    () => null,
  )
