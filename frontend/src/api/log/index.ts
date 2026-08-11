import type {
  BatchLogIdsPayload,
  LogListFilters,
  LogListQuery,
  LogPage,
  LogType,
  RequestParameters,
} from '@/types'
import { DEFAULT_DATETIME_FORMAT, getDateRange } from '@/utils'
import { requestJson } from '@/utils/request'

import { parseLogPage } from './parsers'

const logListPaths: Record<LogType, string> = {
  login: '/log/login/list',
  operation: '/log/operation/list',
  exception: '/log/exception/list',
}

const getDateRangeParameters = (value: [number, number] | null): RequestParameters => {
  if (!value) {
    return {}
  }

  const startRange = getDateRange(value[0])
  const endRange = getDateRange(value[1])
  if (startRange && endRange) {
    return {
      start_time: startRange.start.format(DEFAULT_DATETIME_FORMAT),
      end_time: endRange.end.format(DEFAULT_DATETIME_FORMAT),
    }
  }

  return {}
}

const createLogListParameters = (
  kind: LogType,
  params: LogListQuery,
  filters: LogListFilters,
): RequestParameters => {
  const parameters: RequestParameters = { page: params.page, size: params.size }
  const username = filters.username.trim()
  const path = filters.path.trim()
  if (username) {
    parameters.username = username
  }
  if (kind !== 'login' && path) {
    parameters.path = path
  }
  if (kind === 'login' && filters.status !== null) {
    parameters.status = filters.status
  }

  return { ...parameters, ...getDateRangeParameters(filters.time_range) }
}

export const fetchLogList = (
  kind: LogType,
  params: LogListQuery,
  filters: LogListFilters,
): Promise<LogPage> =>
  requestJson(
    logListPaths[kind],
    { params: createLogListParameters(kind, params, filters) },
    (value) => parseLogPage(value, kind),
  )

export const deleteLogs = (kind: LogType, payload: BatchLogIdsPayload): Promise<null> =>
  requestJson(`/log/${kind}/batch`, { method: 'DELETE', data: payload }, () => null)
