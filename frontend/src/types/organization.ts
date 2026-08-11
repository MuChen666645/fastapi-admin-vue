import type { PaginationResult } from './pagination'

export type DepartmentStatus = '0' | '1'

export type DepartmentFormMode = 'create' | 'edit'

export interface DepartmentOption {
  dept_id: number
  dept_name: string
  status: DepartmentStatus
  children: DepartmentOption[]
}

export interface DepartmentListItem {
  dept_id: number
  parent_id: number | null
  ancestors: string
  dept_name: string
  order_num: number
  leader: string | null
  phone: string | null
  email: string | null
  status: DepartmentStatus
  create_time: string
  update_time: string
  children: DepartmentListItem[]
}

export type DepartmentDetail = Omit<DepartmentListItem, 'children'>

export interface DepartmentListFilters {
  [key: string]: unknown
  name: string
  status: DepartmentStatus | null
}

export interface DepartmentCreatePayload {
  parent_id: number | null
  dept_name: string
  order_num: number
  leader: string | null
  phone: string | null
  email: string | null
  status: DepartmentStatus
}

export type DepartmentUpdatePayload = DepartmentCreatePayload

export type DepartmentFormModel = Record<string, unknown> & {
  parent_id: number
  dept_name: string
  order_num: number
  leader: string
  phone: string
  email: string
  status: DepartmentStatus
}

export interface DepartmentActionPermissions {
  list: boolean
  query: boolean
  create: boolean
  edit: boolean
  remove: boolean
}

export interface DepartmentParentTreeOption {
  key: number
  label: string
  disabled?: boolean
  children?: DepartmentParentTreeOption[]
}

export interface DepartmentPageHeaderProps {
  title: string
  description: string
  total: string
  refreshLoading: boolean
  permissions: DepartmentActionPermissions
}

export interface DepartmentSearchPanelProps {
  model: DepartmentListFilters
  initialValues: DepartmentListFilters
  loading: boolean
}

export interface DepartmentTableProps {
  data: DepartmentListItem[]
  loading: boolean
  permissions: DepartmentActionPermissions
}

export interface DepartmentDetailModalProps {
  show: boolean
  loading: boolean
  item: DepartmentDetail | null
  parentName: string
}

export interface DepartmentFormModalProps {
  show: boolean
  mode: DepartmentFormMode
  model: DepartmentFormModel
  loading: boolean
  departments: DepartmentListItem[]
  editingId: number | null
}

export interface DepartmentCascaderOption {
  label: string
  value: number
  disabled?: boolean
  children?: DepartmentCascaderOption[]
}

export interface PostOption {
  post_id: number
  post_code: string
  post_name: string
  status: DepartmentStatus
}

export type PostPage = PaginationResult<PostOption>
