import type { PaginationRequest, PaginationResult } from './pagination'

export type LogType = 'login' | 'operation' | 'exception'

export type LogStatus = '0' | '1'

export interface LoginLogItem {
  id: number
  user_id: number | null
  username: string
  ip_address: string | null
  user_agent: string | null
  status: LogStatus
  message: string | null
  login_time: string
}

export interface OperationLogItem {
  id: number
  user_id: number | null
  username: string | null
  method: string
  path: string
  ip_address: string | null
  user_agent: string | null
  status_code: number
  duration_ms: number
  operation_time: string
}

export interface ExceptionLogItem {
  id: number
  user_id: number | null
  username: string | null
  method: string
  path: string
  ip_address: string | null
  exception_type: string
  exception_message: string
  traceback: string | null
  exception_time: string
}

export type LogListItem = LoginLogItem | OperationLogItem | ExceptionLogItem

export interface LogListFilters {
  [key: string]: unknown
  username: string
  status: LogStatus | null
  path: string
  time_range: [number, number] | null
}

export type LogListQuery = PaginationRequest

export interface BatchLogIdsPayload {
  ids: number[]
}

export interface LogActionPermissions {
  loginList: boolean
  operationList: boolean
  exceptionList: boolean
  remove: boolean
}

export interface LogPageHeaderProps {
  availableTypes: LogType[]
  activeType: LogType
  total: string
  refreshLoading: boolean
}

export interface LogSearchPanelProps {
  model: LogListFilters
  initialValues: LogListFilters
  loading: boolean
  activeType: LogType
}

export interface LogTableProps {
  kind: LogType
  data: LogListItem[]
  loading: boolean
  selectedRowKeys: number[]
}

export interface LogDetailModalProps {
  show: boolean
  kind: LogType
  item: LogListItem | null
}

export interface LogBatchActionsProps {
  selectedCount: number
  loading: boolean
  disabled: boolean
}

export type LogPage = PaginationResult<LogListItem>
