import type {
  PaginationResult,
  RoleDataScope,
  RoleDetail,
  RoleImportResult,
  RoleListItem,
  RoleOption,
} from '@/types'
import { isRecord, readNumber, readString, requireNumber, requireString } from '@/utils/guards/api'

const parseStatus = (value: unknown): '0' | '1' => {
  const status = requireString(value, 'status')
  if (status !== '0' && status !== '1') {
    throw new Error('接口字段 status 无效')
  }

  return status
}

const parseDataScope = (value: unknown): RoleDataScope => {
  const dataScope = requireString(value, 'data_scope') as RoleDataScope
  if (!['1', '2', '3', '4', '5'].includes(dataScope)) {
    throw new Error('接口字段 data_scope 无效')
  }

  return dataScope
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

const parseRoleListItem = (value: unknown): RoleListItem => {
  const role = parseRole(value)
  if (!isRecord(value)) {
    throw new Error('角色数据无效')
  }

  return {
    ...role,
    data_scope: parseDataScope(value.data_scope),
    version: requireNumber(value.version, 'version'),
    create_time: requireString(value.create_time, 'create_time'),
    update_time: requireString(value.update_time, 'update_time'),
  }
}

const parseNumberList = (value: unknown, fieldName: string): number[] => {
  if (!Array.isArray(value) || value.some((item) => typeof item !== 'number')) {
    throw new Error(`接口字段 ${fieldName} 无效`)
  }

  return value.map((item) => requireNumber(item, fieldName))
}

const parseStringList = (value: unknown, fieldName: string): string[] => {
  if (!Array.isArray(value) || value.some((item) => typeof item !== 'string')) {
    throw new Error(`接口字段 ${fieldName} 无效`)
  }

  return value.map((item) => requireString(item, fieldName))
}

export const parseRoleOptions = (value: unknown): RoleOption[] => {
  if (!Array.isArray(value)) {
    throw new Error('角色下拉列表响应无效')
  }

  return value.map(parseRole).filter((role) => role.code.trim().toLowerCase() !== 'admin')
}

export const parseRolePage = (value: unknown): PaginationResult<RoleListItem> => {
  if (!isRecord(value) || !Array.isArray(value.items)) {
    throw new Error('角色分页响应无效')
  }

  return {
    items: value.items.map(parseRoleListItem),
    total: parsePageNumber(value.total, 'total', 0),
    page: parsePageNumber(value.page, 'page', 1),
    size: parsePageNumber(value.size, 'size', 1),
    pages: parsePageNumber(value.pages, 'pages', 0),
  }
}

export const parseRoleDetail = (value: unknown): RoleDetail => {
  if (!isRecord(value)) {
    throw new Error('角色详情响应无效')
  }

  return {
    ...parseRoleListItem(value),
    menu_ids: parseNumberList(value.menu_ids, 'menu_ids'),
    dept_ids: parseNumberList(value.dept_ids, 'dept_ids'),
    field_permission_codes: parseStringList(value.field_permission_codes, 'field_permission_codes'),
  }
}

export const parseRoleImportResult = (value: unknown): RoleImportResult => {
  if (!isRecord(value)) {
    throw new Error('角色导入结果无效')
  }

  const errors = Array.isArray(value.errors)
    ? value.errors.flatMap((item) => {
        if (!isRecord(item) || typeof item.row !== 'number' || typeof item.message !== 'string') {
          return []
        }
        return [{ row: item.row, message: item.message }]
      })
    : []

  const imported = readNumber(value.imported)
  const failed = readNumber(value.failed)
  if (imported === null || failed === null) {
    throw new Error('接口字段 imported 或 failed 无效')
  }

  return { imported, failed, errors }
}
