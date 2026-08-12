import type {
  RequestParameters,
  ScheduledJob,
  ScheduledJobCreatePayload,
  ScheduledJobFilters,
  ScheduledJobListQuery,
  ScheduledJobLogPage,
  ScheduledJobPage,
  ScheduledJobRunResult,
  ScheduledJobUpdatePayload,
} from '@/types'
import { requestJson } from '@/utils/request'

import {
  parseScheduledJobDetail,
  parseScheduledJobLogPage,
  parseScheduledJobPage,
  parseScheduledJobRunResult,
} from './parsers'

const createScheduledJobParameters = (
  query: ScheduledJobListQuery,
  filters: ScheduledJobFilters,
): RequestParameters => {
  const parameters: RequestParameters = { page: query.page, size: query.size }
  const name = filters.name.trim()

  if (name) {
    parameters.name = name
  }
  if (filters.status) {
    parameters.status = filters.status
  }

  return parameters
}

export const fetchScheduledJobs = (
  query: ScheduledJobListQuery,
  filters: ScheduledJobFilters,
): Promise<ScheduledJobPage> =>
  requestJson(
    '/job/list',
    { params: createScheduledJobParameters(query, filters) },
    parseScheduledJobPage,
  )

export const createScheduledJob = (payload: ScheduledJobCreatePayload): Promise<null> =>
  requestJson('/job/add', { method: 'POST', data: payload }, () => null)

export const fetchScheduledJobDetail = (jobId: number): Promise<ScheduledJob> =>
  requestJson(`/job/${jobId}`, {}, parseScheduledJobDetail)

export const updateScheduledJob = (
  jobId: number,
  payload: ScheduledJobUpdatePayload,
): Promise<null> => requestJson(`/job/${jobId}`, { method: 'PUT', data: payload }, () => null)

export const deleteScheduledJob = (jobId: number): Promise<null> =>
  requestJson(`/job/${jobId}`, { method: 'DELETE' }, () => null)

export const runScheduledJob = (
  jobId: number,
  requestTimeout: number,
): Promise<ScheduledJobRunResult> =>
  requestJson(
    `/job/${jobId}/run`,
    { method: 'POST', timeout: requestTimeout },
    parseScheduledJobRunResult,
  )

export const fetchScheduledJobLogs = (
  jobId: number,
  query: ScheduledJobListQuery,
): Promise<ScheduledJobLogPage> =>
  requestJson(
    `/job/${jobId}/log/list`,
    { params: { page: query.page, size: query.size } },
    parseScheduledJobLogPage,
  )
