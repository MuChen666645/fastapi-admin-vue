import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

const fetchDictDataByType = vi.hoisted(() => vi.fn())

vi.mock('@/api/dictionary', () => ({ fetchDictDataByType }))

import { useDictionaryStore } from '@/stores'

const dictData = {
  dict_code: 2,
  dict_sort: 1,
  dict_label: '男',
  dict_value: '0',
  dict_type: 'sys_user_sex',
  status: '1' as const,
  remark: null,
  create_time: '2026-08-10T09:00:00+08:00',
  update_time: '2026-08-10T10:00:00+08:00',
}

describe('字典 Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    fetchDictDataByType.mockReset()
    fetchDictDataByType.mockResolvedValue([dictData])
  })

  it('优先返回已缓存数据并缓存空数组', async () => {
    fetchDictDataByType.mockResolvedValueOnce([])
    const store = useDictionaryStore()

    await expect(store.load('sys_empty')).resolves.toEqual([])
    await expect(store.load('sys_empty')).resolves.toEqual([])

    expect(fetchDictDataByType).toHaveBeenCalledOnce()
    expect(store.peek('sys_empty')).toEqual([])
  })

  it('合并同一类型的并发请求并支持强制刷新', async () => {
    const store = useDictionaryStore()

    const [firstResult, secondResult] = await Promise.all([
      store.load('sys_user_sex'),
      store.load('sys_user_sex'),
    ])
    await store.load('sys_user_sex', true)

    expect(firstResult).toEqual([dictData])
    expect(secondResult).toEqual([dictData])
    expect(fetchDictDataByType).toHaveBeenCalledTimes(2)
  })

  it('清理缓存后不会被已发出的旧请求重新写入', async () => {
    const store = useDictionaryStore()

    const request = store.load('sys_user_sex')
    store.clear()
    await request

    expect(store.peek('sys_user_sex')).toBeUndefined()
    expect(store.isLoading('sys_user_sex')).toBe(false)
  })

  it('记录请求错误且不把失败结果写入缓存', async () => {
    const requestError = new Error('network failed')
    fetchDictDataByType.mockRejectedValueOnce(requestError)
    const store = useDictionaryStore()

    await expect(store.load('sys_user_sex')).rejects.toBe(requestError)

    expect(store.peek('sys_user_sex')).toBeUndefined()
    expect(store.getError('sys_user_sex')).toBe(requestError)
    expect(store.isLoading('sys_user_sex')).toBe(false)
  })
})
