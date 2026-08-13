import type { PaginationRequest, PaginationResult } from './pagination'

export type SystemConfigFormMode = 'create' | 'edit'

export interface SystemConfig {
  id: number
  config_name: string
  config_key: string
  config_value: string | null
  config_type: string
  is_builtin: boolean
  remark: string | null
  create_time: string
  update_time: string
}

export interface SystemConfigFilters {
  [key: string]: unknown
  name: string
  key: string
}

export type SystemConfigListQuery = PaginationRequest
export type SystemConfigPage = PaginationResult<SystemConfig>

export interface SystemConfigCreatePayload {
  config_name: string
  config_key: string
  config_value: string | null
  config_type: string
  is_builtin: boolean
  remark: string | null
}

export type SystemConfigUpdatePayload = Omit<SystemConfigCreatePayload, 'config_key' | 'is_builtin'>

export interface SystemConfigFormModel extends Record<string, unknown> {
  config_name: string
  config_key: string
  config_value: string
  config_type: string
  is_builtin: boolean
  remark: string
}

export interface SystemConfigActionPermissions {
  list: boolean
  query: boolean
  create: boolean
  edit: boolean
  remove: boolean
  removeBuiltin: boolean
}

export interface SystemConfigSearchPanelProps {
  model: SystemConfigFilters
  initialValues: SystemConfigFilters
  loading: boolean
}

export interface SystemConfigTableProps {
  data: SystemConfig[]
  loading: boolean
  permissions: SystemConfigActionPermissions
}

export interface SystemConfigFormModalProps {
  show: boolean
  mode: SystemConfigFormMode
  model: SystemConfigFormModel
  loading: boolean
}

export interface SystemConfigDetailModalProps {
  show: boolean
  loading: boolean
  item: SystemConfig | null
}
