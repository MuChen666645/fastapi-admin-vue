import type {
  ScheduledJob,
  ScheduledJobLog,
  ScheduledJobLogPage,
  ScheduledJobPage,
  ScheduledJobRunResult,
  ScheduledJobStatus,
} from '@/types'
import { isRecord, readString, requireNumber, requireString } from '@/utils/guards/api'

const parseInteger = (
  value: unknown,
  fieldName: string,
  minimum: number,
  maximum?: number,
): number => {
  const number = requireNumber(value, fieldName)
  if (
    !Number.isInteger(number) ||
    number < minimum ||
    (maximum !== undefined && number > maximum)
  ) {
    throw new Error(`接口字段 ${fieldName} 无效`)
  }

  return number
}

const parseNullableInteger = (
  value: unknown,
  fieldName: string,
  minimum: number,
): number | null => {
  if (value === null || value === undefined) {
    return null
  }

  return parseInteger(value, fieldName, minimum)
}

const parseStatus = (value: unknown): ScheduledJobStatus => {
  const status = requireString(value, 'status')
  if (status !== '0' && status !== '1') {
    throw new Error('接口字段 status 无效')
  }

  return status
}

const parseScheduledJob = (value: unknown): ScheduledJob => {
  if (!isRecord(value)) {
    throw new Error('定时任务数据无效')
  }

  return {
    id: parseInteger(value.id, 'id', 1),
    job_name: requireString(value.job_name, 'job_name'),
    job_key: requireString(value.job_key, 'job_key'),
    task_name: requireString(value.task_name, 'task_name'),
    cron_expression: requireString(value.cron_expression, 'cron_expression'),
    args_json: requireString(value.args_json, 'args_json'),
    timeout_seconds: parseInteger(value.timeout_seconds, 'timeout_seconds', 1, 86_400),
    max_retries: parseInteger(value.max_retries, 'max_retries', 0, 10),
    status: parseStatus(value.status),
    last_run_time: readString(value.last_run_time),
    next_run_time: readString(value.next_run_time),
    last_status: readString(value.last_status),
    last_message: readString(value.last_message),
    create_by: parseNullableInteger(value.create_by, 'create_by', 1),
    create_time: requireString(value.create_time, 'create_time'),
    update_time: requireString(value.update_time, 'update_time'),
  }
}

const parseScheduledJobLog = (value: unknown): ScheduledJobLog => {
  if (!isRecord(value)) {
    throw new Error('任务执行日志数据无效')
  }

  return {
    id: parseInteger(value.id, 'id', 1),
    job_id: parseNullableInteger(value.job_id, 'job_id', 1),
    task_name: requireString(value.task_name, 'task_name'),
    status: requireString(value.status, 'status'),
    message: readString(value.message),
    start_time: requireString(value.start_time, 'start_time'),
    end_time: readString(value.end_time),
    duration_ms: parseNullableInteger(value.duration_ms, 'duration_ms', 0),
  }
}

const parsePage = <T>(value: unknown, itemParser: (item: unknown) => T, errorMessage: string) => {
  if (!isRecord(value) || !Array.isArray(value.items)) {
    throw new Error(errorMessage)
  }

  return {
    items: value.items.map(itemParser),
    total: parseInteger(value.total, 'total', 0),
    page: parseInteger(value.page, 'page', 1),
    size: parseInteger(value.size, 'size', 1),
    pages: parseInteger(value.pages, 'pages', 0),
  }
}

export const parseScheduledJobPage = (value: unknown): ScheduledJobPage =>
  parsePage(value, parseScheduledJob, '定时任务分页响应无效')

export const parseScheduledJobDetail = (value: unknown): ScheduledJob => parseScheduledJob(value)

export const parseScheduledJobLogPage = (value: unknown): ScheduledJobLogPage =>
  parsePage(value, parseScheduledJobLog, '任务执行日志分页响应无效')

export const parseScheduledJobRunResult = (value: unknown): ScheduledJobRunResult => {
  if (!isRecord(value)) {
    throw new Error('任务执行响应无效')
  }

  return {
    job_id: parseInteger(value.job_id, 'job_id', 1),
    status: requireString(value.status, 'status'),
    message: readString(value.message),
  }
}
