import type { SystemConfig, SystemConfigPage } from '@/types'
import { isRecord, requireBoolean, requireNumber, requireString } from '@/utils/guards/api'

const parsePositiveInteger = (value: unknown, fieldName: string): number => {
  const number = requireNumber(value, fieldName)
  if (!Number.isInteger(number) || number < 1) {
    throw new Error(`接口字段 ${fieldName} 无效`)
  }

  return number
}

const parseNonNegativeInteger = (value: unknown, fieldName: string): number => {
  const number = requireNumber(value, fieldName)
  if (!Number.isInteger(number) || number < 0) {
    throw new Error(`接口字段 ${fieldName} 无效`)
  }

  return number
}

const parseNullableString = (value: unknown, fieldName: string): string | null => {
  if (value === null || value === undefined) {
    return null
  }
  if (typeof value !== 'string') {
    throw new Error(`接口字段 ${fieldName} 无效`)
  }

  return value
}

export const parseSystemConfig = (value: unknown): SystemConfig => {
  if (!isRecord(value)) {
    throw new Error('系统参数数据无效')
  }

  return {
    id: parsePositiveInteger(value.id, 'id'),
    config_name: requireString(value.config_name, 'config_name'),
    config_key: requireString(value.config_key, 'config_key'),
    config_value: parseNullableString(value.config_value, 'config_value'),
    config_type: requireString(value.config_type, 'config_type'),
    is_builtin: requireBoolean(value.is_builtin, 'is_builtin'),
    remark: parseNullableString(value.remark, 'remark'),
    create_time: requireString(value.create_time, 'create_time'),
    update_time: requireString(value.update_time, 'update_time'),
  }
}

export const parseSystemConfigPage = (value: unknown): SystemConfigPage => {
  if (!isRecord(value) || !Array.isArray(value.items)) {
    throw new Error('系统参数分页响应无效')
  }

  return {
    items: value.items.map(parseSystemConfig),
    total: parseNonNegativeInteger(value.total, 'total'),
    page: parsePositiveInteger(value.page, 'page'),
    size: parsePositiveInteger(value.size, 'size'),
    pages: parseNonNegativeInteger(value.pages, 'pages'),
  }
}
