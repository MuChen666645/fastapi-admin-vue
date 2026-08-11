import type {
  ExceptionLogItem,
  LogListItem,
  LogPage,
  LogStatus,
  LogType,
  LoginLogItem,
  OperationLogItem,
} from '@/types'
import { isRecord, readString, requireNumber, requireString } from '@/utils/guards/api'

const parseInteger = (value: unknown, fieldName: string): number => {
  const number = requireNumber(value, fieldName)
  if (!Number.isInteger(number)) {
    throw new Error(`接口字段 ${fieldName} 无效`)
  }

  return number
}

const parseNullableInteger = (value: unknown, fieldName: string): number | null => {
  if (value === null || value === undefined) {
    return null
  }

  return parseInteger(value, fieldName)
}

const parseStatus = (value: unknown): LogStatus => {
  const status = requireString(value, 'status')
  if (status !== '0' && status !== '1') {
    throw new Error('接口字段 status 无效')
  }

  return status
}

const parsePageNumber = (value: unknown, fieldName: string, minimum: number): number => {
  const number = parseInteger(value, fieldName)
  if (number < minimum) {
    throw new Error(`接口字段 ${fieldName} 无效`)
  }

  return number
}

const parseLoginLog = (value: unknown): LoginLogItem => {
  if (!isRecord(value)) {
    throw new Error('登录日志数据无效')
  }

  return {
    id: parseInteger(value.id, 'id'),
    user_id: parseNullableInteger(value.user_id, 'user_id'),
    username: requireString(value.username, 'username'),
    ip_address: readString(value.ip_address),
    user_agent: readString(value.user_agent),
    status: parseStatus(value.status),
    message: readString(value.message),
    login_time: requireString(value.login_time, 'login_time'),
  }
}

const parseOperationLog = (value: unknown): OperationLogItem => {
  if (!isRecord(value)) {
    throw new Error('操作日志数据无效')
  }

  return {
    id: parseInteger(value.id, 'id'),
    user_id: parseNullableInteger(value.user_id, 'user_id'),
    username: readString(value.username),
    method: requireString(value.method, 'method'),
    path: requireString(value.path, 'path'),
    ip_address: readString(value.ip_address),
    user_agent: readString(value.user_agent),
    status_code: parseInteger(value.status_code, 'status_code'),
    duration_ms: parseInteger(value.duration_ms, 'duration_ms'),
    operation_time: requireString(value.operation_time, 'operation_time'),
  }
}

const parseExceptionLog = (value: unknown): ExceptionLogItem => {
  if (!isRecord(value)) {
    throw new Error('异常日志数据无效')
  }

  return {
    id: parseInteger(value.id, 'id'),
    user_id: parseNullableInteger(value.user_id, 'user_id'),
    username: readString(value.username),
    method: requireString(value.method, 'method'),
    path: requireString(value.path, 'path'),
    ip_address: readString(value.ip_address),
    exception_type: requireString(value.exception_type, 'exception_type'),
    exception_message: requireString(value.exception_message, 'exception_message'),
    traceback: readString(value.traceback),
    exception_time: requireString(value.exception_time, 'exception_time'),
  }
}

const parseLogItem = (value: unknown, kind: LogType): LogListItem => {
  if (kind === 'login') {
    return parseLoginLog(value)
  }

  if (kind === 'operation') {
    return parseOperationLog(value)
  }

  return parseExceptionLog(value)
}

export const parseLogPage = (value: unknown, kind: LogType): LogPage => {
  if (!isRecord(value) || !Array.isArray(value.items)) {
    throw new Error('日志分页响应无效')
  }

  return {
    items: value.items.map((item) => parseLogItem(item, kind)),
    total: parsePageNumber(value.total, 'total', 0),
    page: parsePageNumber(value.page, 'page', 1),
    size: parsePageNumber(value.size, 'size', 1),
    pages: parsePageNumber(value.pages, 'pages', 0),
  }
}
