import type { UserOption } from './user'

export type TenantFormMode = 'create' | 'edit'
export type TenantStatus = '0' | '1'

export interface Tenant {
  id: number
  code: string
  name: string
  description: string | null
  status: TenantStatus
  version: number
  deleted_at: string | null
  create_time: string
  update_time: string
}

export interface TenantMember {
  user_id: number
  tenant_id: number
  username: string
  nickname: string | null
  status: TenantStatus
  is_default: boolean
  version: number
}

export interface TenantCreatePayload {
  code: string
  name: string
  description: string | null
}

export interface TenantUpdatePayload {
  name: string
  description: string | null
  status: TenantStatus
  version: number
}

export interface TenantMemberAddPayload {
  user_id: number
  is_default: boolean
}

export interface TenantMemberUpdatePayload {
  status: TenantStatus
  is_default: boolean
  version: number
}

export interface TenantFilters extends Record<string, unknown> {
  code: string
  name: string
  status: TenantStatus | null
}

export interface TenantFormModel extends Record<string, unknown> {
  code: string
  name: string
  description: string
  status: TenantStatus
}

export interface TenantMemberAddFormModel extends Record<string, unknown> {
  user_id: number | null
  is_default: boolean
}

export interface TenantActionPermissions {
  list: boolean
  create: boolean
  edit: boolean
  remove: boolean
  memberList: boolean
  memberAdd: boolean
  memberEdit: boolean
  memberRemove: boolean
}

export interface TenantSearchPanelProps {
  model: TenantFilters
  initialValues: TenantFilters
  loading: boolean
}

export interface TenantTableProps {
  data: Tenant[]
  loading: boolean
  permissions: TenantActionPermissions
}

export interface TenantFormModalProps {
  show: boolean
  mode: TenantFormMode
  model: TenantFormModel
  loading: boolean
}

export interface TenantDetailModalProps {
  show: boolean
  item: Tenant | null
}

export interface TenantMemberModalProps {
  show: boolean
  tenant: Tenant | null
  members: TenantMember[]
  userOptions: UserOption[]
  userOptionsLoading: boolean
  canSelectUsers: boolean
  loading: boolean
  addModel: TenantMemberAddFormModel
  permissions: TenantActionPermissions
}
