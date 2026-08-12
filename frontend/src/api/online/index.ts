import type {
  ForceLogoutUserResult,
  OnlineSessionFilters,
  OnlineSessionListQuery,
  OnlineSessionPage,
  RequestParameters,
} from '@/types'
import { requestJson } from '@/utils/request'

import { parseForceLogoutUserResult, parseOnlineSessionPage } from './parsers'

const createOnlineSessionParameters = (
  query: OnlineSessionListQuery,
  filters: OnlineSessionFilters,
): RequestParameters => {
  const parameters: RequestParameters = { page: query.page, size: query.size }
  const username = filters.username.trim()
  const ipAddress = filters.ip_address.trim()

  if (username) {
    parameters.username = username
  }
  if (ipAddress) {
    parameters.ip_address = ipAddress
  }

  return parameters
}

export const fetchOnlineSessions = (
  query: OnlineSessionListQuery,
  filters: OnlineSessionFilters,
): Promise<OnlineSessionPage> =>
  requestJson(
    '/online/list',
    { params: createOnlineSessionParameters(query, filters) },
    parseOnlineSessionPage,
  )

export const forceLogoutSession = (tokenId: string): Promise<null> =>
  requestJson(`/online/token/${encodeURIComponent(tokenId)}`, { method: 'DELETE' }, () => null)

export const forceLogoutUser = (userId: number): Promise<ForceLogoutUserResult> =>
  requestJson(`/online/user/${userId}`, { method: 'DELETE' }, parseForceLogoutUserResult)
