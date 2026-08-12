import type { PaginationBinding, PaginationRequest, PaginationResult } from './pagination'

export type ScheduledJobStatus = '0' | '1'
export type ScheduledJobFormMode = 'create' | 'edit'

export interface ScheduledJob {
  id: number
  job_name: string
  job_key: string
  task_name: string
  cron_expression: string
  args_json: string
  timeout_seconds: number
  max_retries: number
  status: ScheduledJobStatus
  last_run_time: string | null
  next_run_time: string | null
  last_status: string | null
  last_message: string | null
  create_by: number | null
  create_time: string
  update_time: string
}

export interface ScheduledJobLog {
  id: number
  job_id: number | null
  task_name: string
  status: string
  message: string | null
  start_time: string
  end_time: string | null
  duration_ms: number | null
}

export interface ScheduledJobRunResult {
  job_id: number
  status: string
  message: string | null
}

export interface ScheduledJobFilters {
  [key: string]: unknown
  name: string
  status: ScheduledJobStatus | null
}

export type ScheduledJobListQuery = PaginationRequest
export type ScheduledJobPage = PaginationResult<ScheduledJob>
export type ScheduledJobLogPage = PaginationResult<ScheduledJobLog>

export interface ScheduledJobCreatePayload {
  job_name: string
  job_key: string
  task_name: string
  cron_expression: string
  args_json: string
  timeout_seconds: number
  max_retries: number
  status: ScheduledJobStatus
}

export type ScheduledJobUpdatePayload = Omit<ScheduledJobCreatePayload, 'job_key'>

export interface ScheduledJobFormModel extends Record<string, unknown> {
  job_name: string
  job_key: string
  task_name: string
  cron_expression: string
  args_json: string
  timeout_seconds: number
  max_retries: number
  status: ScheduledJobStatus
}

export interface ScheduledJobActionPermissions {
  list: boolean
  query: boolean
  create: boolean
  edit: boolean
  remove: boolean
  run: boolean
}

export interface ScheduledJobPageHeaderProps {
  title: string
  description: string
  total: string
  refreshLoading: boolean
  permissions: ScheduledJobActionPermissions
}

export interface ScheduledJobSearchPanelProps {
  model: ScheduledJobFilters
  initialValues: ScheduledJobFilters
  loading: boolean
}

export interface ScheduledJobTableProps {
  data: ScheduledJob[]
  loading: boolean
  permissions: ScheduledJobActionPermissions
  processingAction: string | null
}

export interface ScheduledJobFormModalProps {
  show: boolean
  mode: ScheduledJobFormMode
  model: ScheduledJobFormModel
  loading: boolean
}

export interface ScheduledJobDetailModalProps {
  show: boolean
  loading: boolean
  item: ScheduledJob | null
}

export interface ScheduledJobLogModalProps {
  show: boolean
  job: ScheduledJob | null
  data: ScheduledJobLog[]
  loading: boolean
  hasError: boolean
  pagination: PaginationBinding
}
