import type {
  DictDataCreatePayload,
  DictDataDetail,
  DictDataListFilters,
  DictDataPage,
  DictDataUpdatePayload,
  DictTypeCreatePayload,
  DictTypeDetail,
  DictTypeListFilters,
  DictTypePage,
  DictTypeUpdatePayload,
  DictionaryImportResult,
  PaginationRequest,
  RequestFileResponse,
  RequestParameters,
} from '@/types'
import { requestBlob, requestJson } from '@/utils/request'

import {
  parseDictDataDetail,
  parseDictDataPage,
  parseDictTypeDetail,
  parseDictTypePage,
  parseDictionaryImportResult,
} from './parsers'

const createTypeListParameters = (
  params: PaginationRequest,
  filters: DictTypeListFilters,
): RequestParameters => {
  const parameters: RequestParameters = { page: params.page, size: params.size }
  const name = filters.name.trim()
  if (name) {
    parameters.name = name
  }
  if (filters.status !== null) {
    parameters.status = filters.status
  }

  return parameters
}

const createDataListParameters = (
  params: PaginationRequest,
  filters: DictDataListFilters,
): RequestParameters => {
  const parameters: RequestParameters = { page: params.page, size: params.size }
  if (filters.dict_type) {
    parameters.dict_type = filters.dict_type
  }
  if (filters.status !== null) {
    parameters.status = filters.status
  }

  return parameters
}

export const fetchDictTypeList = (
  params: PaginationRequest,
  filters: DictTypeListFilters,
): Promise<DictTypePage> =>
  requestJson(
    '/dict/type/list',
    { params: createTypeListParameters(params, filters) },
    parseDictTypePage,
  )

export const fetchDictTypeDetail = (dictId: number): Promise<DictTypeDetail> =>
  requestJson(`/dict/type/${dictId}`, {}, parseDictTypeDetail)

export const createDictType = (payload: DictTypeCreatePayload): Promise<null> =>
  requestJson('/dict/type/add', { method: 'POST', data: payload }, () => null)

export const updateDictType = (dictId: number, payload: DictTypeUpdatePayload): Promise<null> =>
  requestJson(`/dict/type/${dictId}`, { method: 'PUT', data: payload }, () => null)

export const deleteDictType = (dictId: number): Promise<null> =>
  requestJson(`/dict/type/${dictId}`, { method: 'DELETE' }, () => null)

export const fetchDictDataList = (
  params: PaginationRequest,
  filters: DictDataListFilters,
): Promise<DictDataPage> =>
  requestJson(
    '/dict/data/list',
    { params: createDataListParameters(params, filters) },
    parseDictDataPage,
  )

export const fetchDictDataDetail = (dictCode: number): Promise<DictDataDetail> =>
  requestJson(`/dict/data/${dictCode}`, {}, parseDictDataDetail)

export const createDictData = (payload: DictDataCreatePayload): Promise<null> =>
  requestJson('/dict/data/add', { method: 'POST', data: payload }, () => null)

export const updateDictData = (dictCode: number, payload: DictDataUpdatePayload): Promise<null> =>
  requestJson(`/dict/data/${dictCode}`, { method: 'PUT', data: payload }, () => null)

export const deleteDictData = (dictCode: number): Promise<null> =>
  requestJson(`/dict/data/${dictCode}`, { method: 'DELETE' }, () => null)

export const exportDictionary = (): Promise<RequestFileResponse> => requestBlob('/dict/export', {})

export const importDictionary = (file: File): Promise<DictionaryImportResult> => {
  const formData = new FormData()
  formData.append('file', file, file.name)
  return requestJson(
    '/dict/import',
    { method: 'POST', data: formData },
    parseDictionaryImportResult,
  )
}
