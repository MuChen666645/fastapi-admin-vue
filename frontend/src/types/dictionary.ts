import type { PaginationResult } from './pagination'

export type DictionaryStatus = '0' | '1'

export type DictionaryFormMode = 'create' | 'edit'

export interface DictTypeListItem {
  dict_id: number
  dict_name: string
  dict_type: string
  status: DictionaryStatus
  remark: string | null
  create_time: string
  update_time: string
}

export type DictTypeDetail = DictTypeListItem

export interface DictDataListItem {
  dict_code: number
  dict_sort: number
  dict_label: string
  dict_value: string
  dict_type: string
  status: DictionaryStatus
  remark: string | null
  create_time: string
  update_time: string
}

export type DictDataDetail = DictDataListItem

export interface DictTypeListFilters {
  [key: string]: unknown
  name: string
  status: DictionaryStatus | null
}

export interface DictDataListFilters {
  [key: string]: unknown
  dict_type: string | null
  status: DictionaryStatus | null
}

export interface DictTypeCreatePayload {
  dict_name: string
  dict_type: string
  status: DictionaryStatus
  remark: string | null
}

export interface DictTypeUpdatePayload {
  dict_name?: string
  dict_type?: string
  status?: DictionaryStatus
  remark?: string | null
}

export interface DictDataCreatePayload {
  dict_sort: number
  dict_label: string
  dict_value: string
  dict_type: string
  status: DictionaryStatus
  remark: string | null
}

export interface DictDataUpdatePayload {
  dict_sort?: number
  dict_label?: string
  dict_value?: string
  dict_type?: string
  status?: DictionaryStatus
  remark?: string | null
}

export type DictTypePage = PaginationResult<DictTypeListItem>

export type DictDataPage = PaginationResult<DictDataListItem>

export type DictTypeFormModel = Record<string, unknown> & {
  dict_name: string
  dict_type: string
  status: DictionaryStatus
  remark: string
}

export type DictDataFormModel = Record<string, unknown> & {
  dict_sort: number
  dict_label: string
  dict_value: string
  dict_type: string
  status: DictionaryStatus
  remark: string
}

export interface DictionaryImportError {
  row: number
  message: string
}

export interface DictionaryImportResult {
  imported: number
  failed: number
  errors: DictionaryImportError[]
}
