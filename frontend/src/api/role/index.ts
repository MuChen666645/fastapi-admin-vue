import type {
  PaginationResult,
  RequestFileResponse,
  RoleBatchStatusPayload,
  RoleCreatePayload,
  RoleDetail,
  RoleImportResult,
  RoleListFilters,
  RoleListItem,
  RoleListQuery,
  RoleOption,
  RoleUpdatePayload,
} from '@/types'
import { requestBlob, requestJson } from '@/utils/request'

import { parseRoleDetail, parseRoleImportResult, parseRoleOptions, parseRolePage } from './parsers'

export const fetchRoleOptions = (): Promise<RoleOption[]> =>
  requestJson('/role/options', {}, parseRoleOptions)

const createRoleListParameters = (
  params: RoleListQuery,
  filters: RoleListFilters,
): Record<string, string | number> => {
  const parameters: Record<string, string | number> = { page: params.page, size: params.size }
  const name = filters.name.trim()
  const code = filters.code.trim()
  if (name) {
    parameters.name = name
  }
  if (code) {
    parameters.code = code
  }

  return parameters
}

export const fetchRoleList = (
  params: RoleListQuery,
  filters: RoleListFilters,
): Promise<PaginationResult<RoleListItem>> =>
  requestJson('/role/list', { params: createRoleListParameters(params, filters) }, parseRolePage)

export const fetchRoleDetail = (roleId: number): Promise<RoleDetail> =>
  requestJson(`/role/${roleId}`, {}, parseRoleDetail)

export const createRole = (payload: RoleCreatePayload): Promise<null> =>
  requestJson('/role/add', { method: 'POST', data: payload }, () => null)

export const updateRole = (roleId: number, payload: RoleUpdatePayload): Promise<null> =>
  requestJson(`/role/${roleId}`, { method: 'PUT', data: payload }, () => null)

export const deleteRole = (roleId: number): Promise<null> =>
  requestJson(`/role/${roleId}`, { method: 'DELETE' }, () => null)

export const batchUpdateRoleStatus = (payload: RoleBatchStatusPayload): Promise<null> =>
  requestJson('/role/batch/status', { method: 'PUT', data: payload }, () => null)

export const exportRoles = (): Promise<RequestFileResponse> => requestBlob('/role/export', {})

export const importRoles = (file: File): Promise<RoleImportResult> => {
  const formData = new FormData()
  formData.append('file', file, file.name)
  return requestJson('/role/import', { method: 'POST', data: formData }, parseRoleImportResult)
}
