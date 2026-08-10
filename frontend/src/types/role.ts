import type { PaginationResult } from './pagination'

export type RoleStatus = '0' | '1'

export type RoleDataScope = '1' | '2' | '3' | '4' | '5'

export type RoleFormMode = 'create' | 'edit'

export interface RoleOption {
  id: number
  name: string
  code: string
  description: string | null
  status: RoleStatus
}

export interface RoleListItem {
  id: number
  name: string
  code: string
  description: string | null
  data_scope: RoleDataScope
  status: RoleStatus
  version: number
  create_time: string
  update_time: string
}

export interface RoleDetail extends RoleListItem {
  menu_ids: number[]
  dept_ids: number[]
  field_permission_codes: string[]
}

export interface RoleListFilters {
  [key: string]: unknown
  name: string
  code: string
}

export interface RoleListQuery {
  page: number
  size: number
}

export interface RoleCreatePayload {
  name: string
  code: string
  description: string | null
  data_scope: RoleDataScope
  menu_ids: number[]
  dept_ids: number[]
  field_permission_codes: string[]
}

export interface RoleUpdatePayload {
  name?: string
  code?: string
  description?: string | null
  data_scope?: RoleDataScope
  status?: RoleStatus
  version?: number
  menu_ids?: number[]
  dept_ids?: number[]
  field_permission_codes: string[]
}

export interface RoleBatchStatusPayload {
  role_ids: number[]
  status: RoleStatus
}

export interface RoleImportError {
  row: number
  message: string
}

export interface RoleImportResult {
  imported: number
  failed: number
  errors: RoleImportError[]
}

export type RoleFormModel = Record<string, unknown> & {
  name: string
  code: string
  description: string
  data_scope: RoleDataScope
  status: RoleStatus
  menu_ids: number[]
  dept_ids: number[]
  field_permission_codes: string[]
  version: number | null
}

export type RolePage = PaginationResult<RoleListItem>
