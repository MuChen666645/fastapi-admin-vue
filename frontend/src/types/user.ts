import type { PaginationRequest } from './pagination'

export type UserStatus = '0' | '1'

export type UserSex = '0' | '1'

export type UserFormMode = 'create' | 'edit'

export interface UserOption {
  id: number
  username: string
  nickname: string | null
}

export interface UserListItem {
  id: number
  create_time: string
  username: string
  email: string | null
  phone: string | null
  role_id: number | null
  dept_id: number | null
  nickname: string | null
  sex: UserSex | null
  avatar: string | null
  update_time: string | null
  status: UserStatus
  version: number | null
}

export interface UserRoleOption {
  id: number
  name: string
  code: string
  description: string | null
  status: UserStatus
}

export interface UserPostOption {
  post_id: number
  post_code: string
  post_name: string
  status: UserStatus
}

export interface UserDepartmentOption {
  dept_id: number
  dept_name: string
  status: UserStatus
  children: UserDepartmentOption[]
}

export interface UserDetail {
  user: UserListItem
  roles: UserRoleOption[]
  posts: UserPostOption[]
  permissions: string[]
}

export interface UserListFilters {
  [key: string]: unknown
  username: string
  nickname: string
  phone: string
  email: string
  create_time: [number, number] | null
}

export interface UserListQuery extends PaginationRequest {
  username?: string
  nickname?: string
  phone?: string
  email?: string
  start_time?: string
  end_time?: string
}

export interface UserCreatePayload {
  username: string
  password: string
  phone: string
  email: string | null
  nickname: string | null
  sex: UserSex | null
  dept_id: number | null
  post_ids: number[]
  role_ids: number[]
}

export interface UserUpdatePayload {
  version?: number
  username?: string
  email?: string | null
  phone?: string | null
  nickname?: string | null
  sex?: UserSex | null
  status?: UserStatus
  dept_id?: number | null
  post_ids?: number[]
}

export interface UserResetPasswordPayload {
  password: string
}

export interface UserImportError {
  row: number
  message: string
}

export interface UserImportResult {
  imported: number
  failed: number
  errors: UserImportError[]
}

export interface UserBatchIdsPayload {
  user_ids: number[]
}

export interface UserBatchStatusPayload extends UserBatchIdsPayload {
  status: UserStatus
}

export interface UserRolePayload {
  role_ids: number[]
}

export type UserFormModel = Record<string, unknown> & {
  username: string
  password: string
  phone: string
  email: string
  nickname: string
  sex: UserSex | null
  status: UserStatus
  dept_id: number | null
  post_ids: number[]
  role_ids: number[]
  version: number | null
}

export type UserResetPasswordModel = Record<string, unknown> & {
  password: string
}
