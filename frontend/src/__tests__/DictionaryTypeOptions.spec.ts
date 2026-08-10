import { flushPromises, mount } from '@vue/test-utils'
import { defineComponent } from 'vue'
import { describe, expect, it, vi } from 'vitest'

const fetchDictTypeList = vi.hoisted(() => vi.fn())

vi.mock('@/api', () => ({ fetchDictTypeList }))

import { useDictionaryTypeOptions } from '@/views/system/dict/useDictionaryTypeOptions'

const createDictType = (dictId: number, dictType: string) => ({
  dict_id: dictId,
  dict_name: `字典${dictId}`,
  dict_type: dictType,
  status: '1' as const,
  remark: null,
  create_time: '2026-08-10T09:00:00+08:00',
  update_time: '2026-08-10T09:00:00+08:00',
})

describe('useDictionaryTypeOptions', () => {
  it('loads every dictionary type page for data filters and forms', async () => {
    fetchDictTypeList
      .mockResolvedValueOnce({
        items: [createDictType(1, 'sys_user_sex')],
        total: 101,
        page: 1,
        size: 100,
        pages: 2,
      })
      .mockResolvedValueOnce({
        items: [createDictType(2, 'sys_normal_disable')],
        total: 101,
        page: 2,
        size: 100,
        pages: 2,
      })

    let options: ReturnType<typeof useDictionaryTypeOptions> | undefined
    const wrapper = mount(
      defineComponent({
        setup() {
          options = useDictionaryTypeOptions()
          return () => null
        },
      }),
    )

    await flushPromises()

    expect(fetchDictTypeList).toHaveBeenNthCalledWith(
      1,
      { page: 1, size: 100 },
      {
        name: '',
        status: null,
      },
    )
    expect(fetchDictTypeList).toHaveBeenNthCalledWith(
      2,
      { page: 2, size: 100 },
      {
        name: '',
        status: null,
      },
    )
    expect(options?.items.value.map((item) => item.dict_type)).toEqual([
      'sys_user_sex',
      'sys_normal_disable',
    ])

    wrapper.unmount()
  })
})
