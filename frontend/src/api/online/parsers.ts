import type { ForceLogoutUserResult, OnlineSession, OnlineSessionPage } from '@/types'
import { isRecord, readString, requireNumber, requireString } from '@/utils/guards/api'

const parseInteger = (value: unknown, fieldName: string, minimum: number): number => {
  const number = requireNumber(value, fieldName)
  if (!Number.isInteger(number) || number < minimum) {
    throw new Error(`接口字段 ${fieldName} 无效`)
  }

  return number
}

const parseUserId = (value: unknown): number | string => {
  if (typeof value === 'number' && Number.isInteger(value)) {
    return value
  }

  return requireString(value, 'user_id')
}

const parseOnlineSession = (value: unknown): OnlineSession => {
  if (!isRecord(value)) {
    throw new Error('在线会话数据无效')
  }

  const tokenId = requireString(value.token_id, 'token_id')
  if (!/^[a-f0-9]{64}$/.test(tokenId)) {
    throw new Error('接口字段 token_id 无效')
  }

  return {
    token_id: tokenId,
    user_id: parseUserId(value.user_id),
    username: readString(value.username),
    ip_address: readString(value.ip_address),
    user_agent: readString(value.user_agent),
    login_time: readString(value.login_time),
    expire_time: requireString(value.expire_time, 'expire_time'),
  }
}

export const parseOnlineSessionPage = (value: unknown): OnlineSessionPage => {
  if (!isRecord(value) || !Array.isArray(value.items)) {
    throw new Error('在线会话分页响应无效')
  }

  return {
    items: value.items.map(parseOnlineSession),
    total: parseInteger(value.total, 'total', 0),
    page: parseInteger(value.page, 'page', 1),
    size: parseInteger(value.size, 'size', 1),
    pages: parseInteger(value.pages, 'pages', 0),
  }
}

export const parseForceLogoutUserResult = (value: unknown): ForceLogoutUserResult => {
  if (!isRecord(value)) {
    throw new Error('用户强制下线响应无效')
  }

  return {
    user_id: parseInteger(value.user_id, 'user_id', 1),
    revoked_token_count: parseInteger(value.revoked_token_count, 'revoked_token_count', 0),
  }
}
