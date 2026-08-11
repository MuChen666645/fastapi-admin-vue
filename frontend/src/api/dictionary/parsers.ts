import type {
  DictDataDetail,
  DictDataListItem,
  DictTypeDetail,
  DictTypeListItem,
  DictionaryImportResult,
  DictionaryStatus,
  PaginationResult,
} from '@/types'
import { isRecord, readNumber, readString, requireNumber, requireString } from '@/utils/guards/api'

const parseStatus = (value: unknown): DictionaryStatus => {
  const status = requireString(value, 'status')
  if (status !== '0' && status !== '1') {
    throw new Error('接口字段 status 无效')
  }

  return status
}

const parsePageNumber = (value: unknown, fieldName: string, minimum: number): number => {
  const number = typeof value === 'number' ? value : Number.NaN
  if (!Number.isInteger(number) || number < minimum) {
    throw new Error(`接口字段 ${fieldName} 无效`)
  }

  return number
}

const parseDictType = (value: unknown): DictTypeListItem => {
  if (!isRecord(value)) {
    throw new Error('字典类型数据无效')
  }

  return {
    dict_id: requireNumber(value.dict_id, 'dict_id'),
    dict_name: requireString(value.dict_name, 'dict_name'),
    dict_type: requireString(value.dict_type, 'dict_type'),
    status: parseStatus(value.status),
    remark: readString(value.remark),
    create_time: requireString(value.create_time, 'create_time'),
    update_time: requireString(value.update_time, 'update_time'),
  }
}

const parseDictData = (value: unknown): DictDataListItem => {
  if (!isRecord(value)) {
    throw new Error('字典数据无效')
  }

  return {
    dict_code: requireNumber(value.dict_code, 'dict_code'),
    dict_sort: requireNumber(value.dict_sort, 'dict_sort'),
    dict_label: requireString(value.dict_label, 'dict_label'),
    dict_value: requireString(value.dict_value, 'dict_value'),
    dict_type: requireString(value.dict_type, 'dict_type'),
    status: parseStatus(value.status),
    remark: readString(value.remark),
    create_time: requireString(value.create_time, 'create_time'),
    update_time: requireString(value.update_time, 'update_time'),
  }
}

const parsePage = <T>(
  value: unknown,
  parseItem: (item: unknown) => T,
  label: string,
): PaginationResult<T> => {
  if (!isRecord(value) || !Array.isArray(value.items)) {
    throw new Error(`${label}分页响应无效`)
  }

  return {
    items: value.items.map(parseItem),
    total: parsePageNumber(value.total, 'total', 0),
    page: parsePageNumber(value.page, 'page', 1),
    size: parsePageNumber(value.size, 'size', 1),
    pages: parsePageNumber(value.pages, 'pages', 0),
  }
}

export const parseDictTypePage = (value: unknown): PaginationResult<DictTypeListItem> =>
  parsePage(value, parseDictType, '字典类型')

export const parseDictTypeDetail = (value: unknown): DictTypeDetail => parseDictType(value)

export const parseDictDataPage = (value: unknown): PaginationResult<DictDataListItem> =>
  parsePage(value, parseDictData, '字典数据')

export const parseDictDataDetail = (value: unknown): DictDataDetail => parseDictData(value)

export const parseDictDataItems = (value: unknown): DictDataListItem[] => {
  if (!Array.isArray(value)) {
    throw new Error('字典数据列表无效')
  }

  return value.map(parseDictData)
}

export const parseDictionaryImportResult = (value: unknown): DictionaryImportResult => {
  if (!isRecord(value)) {
    throw new Error('字典导入结果无效')
  }

  const imported = readNumber(value.imported)
  const failed = readNumber(value.failed)
  if (imported === null || failed === null) {
    throw new Error('接口字段 imported 或 failed 无效')
  }

  const errors = Array.isArray(value.errors)
    ? value.errors.flatMap((item) => {
        if (!isRecord(item) || typeof item.row !== 'number' || typeof item.message !== 'string') {
          return []
        }
        return [{ row: item.row, message: item.message }]
      })
    : []

  return { imported, failed, errors }
}
