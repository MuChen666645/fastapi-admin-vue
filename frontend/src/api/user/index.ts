import type { CurrentUserResponse, UserRoute } from '@/types'
import { requestJson } from '@/utils/request'

import { parseCurrentUserResponse, parseUserRoutes } from './parsers'

export const fetchCurrentUser = (): Promise<CurrentUserResponse> =>
  requestJson('/user/info', {}, parseCurrentUserResponse)

export const fetchUserRoutes = (): Promise<UserRoute[]> =>
  requestJson('/user/routes', {}, parseUserRoutes)
