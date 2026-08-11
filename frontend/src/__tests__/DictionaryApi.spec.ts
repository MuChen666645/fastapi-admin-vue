import { beforeEach, describe, expect, it, vi } from 'vitest'

const requestJson = vi.hoisted(() => vi.fn())
const requestBlob = vi.hoisted(() => vi.fn())

vi.mock('../utils/request', () => ({ requestBlob, requestJson }))

import {
  createDictData,
  createDictType,
  deleteDictData,
  deleteDictType,
  exportDictionary,
  fetchDictDataByType,
  fetchDictDataDetail,
  fetchDictDataList,
  fetchDictTypeDetail,
  fetchDictTypeList,
  importDictionary,
  updateDictData,
  updateDictType,
} from '@/api/dictionary'
import {
  parseDictDataItems,
  parseDictDataPage,
  parseDictTypePage,
  parseDictionaryImportResult,
} from '@/api/dictionary/parsers'

const dictType = {
  dict_id: 1,
  dict_name: '用户性别',
  dict_type: 'sys_user_sex',
  status: '1',
  remark: null,
  create_time: '2026-08-10T09:00:00+08:00',
  update_time: '2026-08-10T10:00:00+08:00',
}

const dictData = {
  dict_code: 2,
  dict_sort: 1,
  dict_label: '男',
  dict_value: '0',
  dict_type: 'sys_user_sex',
  status: '1',
  remark: null,
  create_time: '2026-08-10T09:00:00+08:00',
  update_time: '2026-08-10T10:00:00+08:00',
}

describe('字典 API', () => {
  beforeEach(() => {
    requestJson.mockReset()
    requestBlob.mockReset()
    requestJson.mockResolvedValue(null)
    requestBlob.mockResolvedValue({ blob: new Blob(['dictionary']), filename: 'dictionary.xlsx' })
  })

  it('按后端契约查询字典类型和字典数据分页', async () => {
    await fetchDictTypeList({ page: 2, size: 20 }, { name: ' 性别 ', status: '1' })
    await fetchDictDataList({ page: 1, size: 50 }, { dict_type: 'sys_user_sex', status: null })

    expect(requestJson).toHaveBeenNthCalledWith(
      1,
      '/dict/type/list',
      { params: { page: 2, size: 20, name: '性别', status: '1' } },
      expect.any(Function),
    )
    expect(requestJson).toHaveBeenNthCalledWith(
      2,
      '/dict/data/list',
      { params: { page: 1, size: 50, dict_type: 'sys_user_sex' } },
      expect.any(Function),
    )
  })

  it('按类型查询登录用户可使用的字典数据', async () => {
    await fetchDictDataByType(' sys_user_sex ')

    expect(requestJson).toHaveBeenCalledWith('/dict/data/type/sys_user_sex', {}, parseDictDataItems)
    await expect(fetchDictDataByType('  ')).rejects.toThrow('字典类型编码不能为空')
  })

  it('调用字典类型、字典数据 CRUD 以及导入导出接口', async () => {
    await fetchDictTypeDetail(1)
    await createDictType({
      dict_name: '用户性别',
      dict_type: 'sys_user_sex',
      status: '1',
      remark: null,
    })
    await updateDictType(1, { dict_type: 'system_user_sex', status: '0' })
    await deleteDictType(1)
    await fetchDictDataDetail(2)
    await createDictData({
      dict_sort: 1,
      dict_label: '男',
      dict_value: '0',
      dict_type: 'sys_user_sex',
      status: '1',
      remark: null,
    })
    await updateDictData(2, { dict_label: '男性', status: '0' })
    await deleteDictData(2)
    await exportDictionary()
    await importDictionary(new File(['dictionary'], 'dictionary.xlsx'))

    expect(requestJson).toHaveBeenNthCalledWith(1, '/dict/type/1', {}, expect.any(Function))
    expect(requestJson).toHaveBeenNthCalledWith(
      2,
      '/dict/type/add',
      expect.objectContaining({ method: 'POST' }),
      expect.any(Function),
    )
    expect(requestJson).toHaveBeenNthCalledWith(
      3,
      '/dict/type/1',
      { method: 'PUT', data: { dict_type: 'system_user_sex', status: '0' } },
      expect.any(Function),
    )
    expect(requestJson).toHaveBeenNthCalledWith(
      4,
      '/dict/type/1',
      { method: 'DELETE' },
      expect.any(Function),
    )
    expect(requestJson).toHaveBeenNthCalledWith(5, '/dict/data/2', {}, expect.any(Function))
    expect(requestJson).toHaveBeenNthCalledWith(
      6,
      '/dict/data/add',
      expect.objectContaining({ method: 'POST' }),
      expect.any(Function),
    )
    expect(requestJson).toHaveBeenNthCalledWith(
      7,
      '/dict/data/2',
      { method: 'PUT', data: { dict_label: '男性', status: '0' } },
      expect.any(Function),
    )
    expect(requestJson).toHaveBeenNthCalledWith(
      8,
      '/dict/data/2',
      { method: 'DELETE' },
      expect.any(Function),
    )
    expect(requestBlob).toHaveBeenCalledWith('/dict/export', {})

    const [, importOptions] = requestJson.mock.calls[8] as [string, { data: FormData }]
    expect(importOptions.data.get('file')).toBeInstanceOf(File)
  })

  it('解析字典分页和导入结果', () => {
    expect(
      parseDictTypePage({ items: [dictType], total: 1, page: 1, size: 20, pages: 1 }),
    ).toMatchObject({ items: [{ dict_type: 'sys_user_sex' }] })
    expect(
      parseDictDataPage({ items: [dictData], total: 1, page: 1, size: 20, pages: 1 }),
    ).toMatchObject({ items: [{ dict_code: 2 }] })
    expect(parseDictDataItems([dictData])).toEqual([dictData])
    expect(() => parseDictDataItems({ items: [dictData] })).toThrow('字典数据列表无效')
    expect(
      parseDictionaryImportResult({
        imported: 2,
        failed: 1,
        errors: [{ row: 3, message: '字典类型不存在' }],
      }),
    ).toEqual({
      imported: 2,
      failed: 1,
      errors: [{ row: 3, message: '字典类型不存在' }],
    })
  })
})
