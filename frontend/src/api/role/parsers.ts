import type { PaginationResult, RoleOption } from '@/types'
import { isRecord, readString, requireNumber, requireString } from '@/utils/guards/api'

const parseStatus = (value: unknown): '0' | '1' => {
  const status = readString(value, '1') ?? '1'
  if (status !== '0' && status !== '1') {
    throw new Error('接口字段 status 无效')
  }

  return status
}

const parsePageNumber = (value: unknown, fieldName: string, minimum: number): number => {
  const number = typeof value === 'number' ? value : Number.NaN
  if (!Number.isInteger(number) || number < minimum) {
    throw new Error(`接口字段 ${fieldName} 无效`)
  }

  return number
}

const parseRole = (value: unknown): RoleOption => {
  if (!isRecord(value)) {
    throw new Error('角色数据无效')
  }

  return {
    id: requireNumber(value.id, 'id'),
    name: requireString(value.name, 'name'),
    code: requireString(value.code, 'code'),
    description: readString(value.description),
    status: parseStatus(value.status),
  }
}

export const parseRoleOptions = (value: unknown): RoleOption[] => {
  if (!Array.isArray(value)) {
    throw new Error('角色下拉列表响应无效')
  }

  return value.map(parseRole).filter((role) => role.code.trim().toLowerCase() !== 'admin')
}

export const parseRolePage = (value: unknown): PaginationResult<RoleOption> => {
  if (!isRecord(value) || !Array.isArray(value.items)) {
    throw new Error('角色分页响应无效')
  }

  return {
    items: value.items.map(parseRole),
    total: parsePageNumber(value.total, 'total', 0),
    page: parsePageNumber(value.page, 'page', 1),
    size: parsePageNumber(value.size, 'size', 1),
    pages: parsePageNumber(value.pages, 'pages', 0),
  }
}
