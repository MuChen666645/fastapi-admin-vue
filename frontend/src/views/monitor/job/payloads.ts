import type {
  ScheduledJobCreatePayload,
  ScheduledJobFormModel,
  ScheduledJobUpdatePayload,
} from '@/types'

const RUN_REQUEST_BUFFER_SECONDS = 30
const BACKEND_MAX_DEFAULT_RETRIES = 10

const normalizeArguments = (value: string): string => {
  const parsed: unknown = JSON.parse(value)
  if (typeof parsed !== 'object' || parsed === null || Array.isArray(parsed)) {
    throw new Error('任务参数必须是 JSON 对象')
  }

  return JSON.stringify(parsed)
}

const createSharedPayload = (model: ScheduledJobFormModel): ScheduledJobUpdatePayload => ({
  job_name: model.job_name.trim(),
  task_name: model.task_name.trim(),
  cron_expression: model.cron_expression.trim().replace(/\s+/g, ' '),
  args_json: normalizeArguments(model.args_json.trim()),
  timeout_seconds: model.timeout_seconds,
  max_retries: model.max_retries,
  status: model.status,
})

export const createScheduledJobPayload = (
  model: ScheduledJobFormModel,
): ScheduledJobCreatePayload => ({
  ...createSharedPayload(model),
  job_key: model.job_key.trim(),
})

export const createScheduledJobUpdatePayload = (
  model: ScheduledJobFormModel,
): ScheduledJobUpdatePayload => createSharedPayload(model)

export const calculateScheduledJobRunTimeout = (
  timeoutSeconds: number,
  maxRetries: number,
): number =>
  (timeoutSeconds * (Math.max(maxRetries, BACKEND_MAX_DEFAULT_RETRIES) + 1) +
    RUN_REQUEST_BUFFER_SECONDS) *
  1_000
