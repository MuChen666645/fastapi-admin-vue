import type {
  RequestParameters,
  SystemConfigCreatePayload,
  SystemConfig,
  SystemConfigFilters,
  SystemConfigListQuery,
  SystemConfigPage,
  SystemConfigUpdatePayload,
} from '@/types'
import { requestJson } from '@/utils/request'

import { parseSystemConfig, parseSystemConfigPage } from './parsers'

const createSystemConfigParameters = (
  query: SystemConfigListQuery,
  filters: SystemConfigFilters,
): RequestParameters => {
  const parameters: RequestParameters = { page: query.page, size: query.size }
  const name = filters.name.trim()
  const key = filters.key.trim()

  if (name) {
    parameters.name = name
  }
  if (key) {
    parameters.key = key
  }

  return parameters
}

export const fetchSystemConfigs = (
  query: SystemConfigListQuery,
  filters: SystemConfigFilters,
): Promise<SystemConfigPage> =>
  requestJson(
    '/config/list',
    { params: createSystemConfigParameters(query, filters) },
    parseSystemConfigPage,
  )

export const fetchSystemConfigDetail = (configId: number): Promise<SystemConfig> =>
  requestJson(`/config/${configId}`, {}, parseSystemConfig)

export const createSystemConfig = (payload: SystemConfigCreatePayload): Promise<null> =>
  requestJson('/config/add', { method: 'POST', data: payload }, () => null)

export const updateSystemConfig = (
  configId: number,
  payload: SystemConfigUpdatePayload,
): Promise<null> => requestJson(`/config/${configId}`, { method: 'PUT', data: payload }, () => null)

export const deleteSystemConfig = (configId: number): Promise<null> =>
  requestJson(`/config/${configId}`, { method: 'DELETE' }, () => null)
