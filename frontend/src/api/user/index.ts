import type {
  CurrentUserResponse,
  UserBatchIdsPayload,
  UserBatchStatusPayload,
  PaginationResult,
  UserCreatePayload,
  UserDetail,
  UserImportResult,
  UserListFilters,
  UserListItem,
  UserListQuery,
  UserOption,
  UserResetPasswordPayload,
  UserRolePayload,
  UserUpdatePayload,
  UserRoute,
  RequestFileResponse,
  RequestParameters,
} from '@/types'
import { DEFAULT_DATETIME_FORMAT, getDateRange } from '@/utils'
import { requestBlob, requestJson } from '@/utils/request'

import {
  parseCurrentUserResponse,
  parseUserDetail,
  parseUserImportResult,
  parseUserListPage,
  parseUserOptions,
  parseUserRoutes,
} from './parsers'

export const fetchCurrentUser = (): Promise<CurrentUserResponse> =>
  requestJson('/user/info', {}, parseCurrentUserResponse)

export const fetchUserRoutes = (): Promise<UserRoute[]> =>
  requestJson('/user/routes', {}, parseUserRoutes)

export const fetchUserOptions = (): Promise<UserOption[]> =>
  requestJson('/user/options', {}, parseUserOptions)

export const exportUsers = (): Promise<RequestFileResponse> => requestBlob('/user/export', {})

export const importUsers = (file: File): Promise<UserImportResult> => {
  const formData = new FormData()
  formData.append('file', file, file.name)
  return requestJson('/user/import', { method: 'POST', data: formData }, parseUserImportResult)
}

export const batchUpdateUserStatus = (payload: UserBatchStatusPayload): Promise<null> =>
  requestJson('/user/batch/status', { method: 'PUT', data: payload }, () => null)

export const batchDeleteUsers = (payload: UserBatchIdsPayload): Promise<null> =>
  requestJson('/user/batch', { method: 'DELETE', data: payload }, () => null)

const getDateRangeParameters = (value: [number, number] | null): RequestParameters => {
  if (!value) {
    return {}
  }

  const startRange = getDateRange(value[0])
  const endRange = getDateRange(value[1])
  if (startRange && endRange) {
    return {
      start_time: startRange.start.format(DEFAULT_DATETIME_FORMAT),
      end_time: endRange.end.format(DEFAULT_DATETIME_FORMAT),
    }
  }

  return {}
}

const createUserListParameters = (
  params: UserListQuery,
  filters: UserListFilters,
): RequestParameters => {
  const parameters: RequestParameters = { page: params.page, size: params.size }
  const textFilters: ReadonlyArray<
    keyof Pick<UserListFilters, 'username' | 'nickname' | 'phone' | 'email'>
  > = ['username', 'nickname', 'phone', 'email']

  textFilters.forEach((key) => {
    const value = filters[key].trim()
    if (value) {
      parameters[key] = value
    }
  })
  return { ...parameters, ...getDateRangeParameters(filters.create_time) }
}

export const fetchUserList = (
  params: UserListQuery,
  filters: UserListFilters,
): Promise<PaginationResult<UserListItem>> =>
  requestJson(
    '/user/list',
    { params: createUserListParameters(params, filters) },
    parseUserListPage,
  )

export const fetchUserDetail = (userId: number): Promise<UserDetail> =>
  requestJson(`/user/${userId}`, {}, parseUserDetail)

export const createUser = (payload: UserCreatePayload): Promise<null> =>
  requestJson('/user/add', { method: 'POST', data: payload }, () => null)

export const updateUser = (userId: number, payload: UserUpdatePayload): Promise<null> =>
  requestJson(`/user/${userId}`, { method: 'PUT', data: payload }, () => null)

export const deleteUser = (userId: number): Promise<null> =>
  requestJson(`/user/${userId}`, { method: 'DELETE' }, () => null)

export const resetUserPassword = (
  userId: number,
  payload: UserResetPasswordPayload,
): Promise<null> =>
  requestJson(`/user/${userId}/reset-password`, { method: 'PUT', data: payload }, () => null)

export const bindUserRoles = (userId: number, payload: UserRolePayload): Promise<null> =>
  requestJson(`/user/${userId}/roles`, { method: 'PUT', data: payload }, () => null)
