import type { Tenant, TenantMember, TenantStatus } from '@/types'
import {
  isRecord,
  readString,
  requireBoolean,
  requireNumber,
  requireString,
} from '@/utils/guards/api'

const parsePositiveInteger = (value: unknown, fieldName: string): number => {
  const number = requireNumber(value, fieldName)
  if (!Number.isInteger(number) || number < 1) {
    throw new Error(`接口字段 ${fieldName} 无效`)
  }

  return number
}

const parseStatus = (value: unknown, fieldName: string): TenantStatus => {
  const status = requireString(value, fieldName)
  if (status !== '0' && status !== '1') {
    throw new Error(`接口字段 ${fieldName} 无效`)
  }

  return status
}

export const parseTenant = (value: unknown): Tenant => {
  if (!isRecord(value)) {
    throw new Error('租户数据无效')
  }

  return {
    id: parsePositiveInteger(value.id, 'id'),
    code: requireString(value.code, 'code'),
    name: requireString(value.name, 'name'),
    description: readString(value.description),
    status: parseStatus(value.status, 'status'),
    version: parsePositiveInteger(value.version, 'version'),
    deleted_at: readString(value.deleted_at),
    create_time: requireString(value.create_time, 'create_time'),
    update_time: requireString(value.update_time, 'update_time'),
  }
}

export const parseTenants = (value: unknown): Tenant[] => {
  if (!Array.isArray(value)) {
    throw new Error('租户列表响应无效')
  }

  return value.map(parseTenant)
}

const parseTenantMember = (value: unknown): TenantMember => {
  if (!isRecord(value)) {
    throw new Error('租户成员数据无效')
  }

  return {
    user_id: parsePositiveInteger(value.user_id, 'user_id'),
    tenant_id: parsePositiveInteger(value.tenant_id, 'tenant_id'),
    username: requireString(value.username, 'username'),
    nickname: readString(value.nickname),
    status: parseStatus(value.status, 'status'),
    is_default: requireBoolean(value.is_default, 'is_default'),
    version: parsePositiveInteger(value.version, 'version'),
  }
}

export const parseTenantMembers = (value: unknown): TenantMember[] => {
  if (!Array.isArray(value)) {
    throw new Error('租户成员列表响应无效')
  }

  return value.map(parseTenantMember)
}

export const parseTenantMemberResult = (value: unknown): TenantMember => parseTenantMember(value)
