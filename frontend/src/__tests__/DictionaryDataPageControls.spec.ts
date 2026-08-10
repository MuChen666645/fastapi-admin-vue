import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import DictionaryPageHeader from '@/views/system/dict/components/DictionaryPageHeader.vue'
import DictDataSearchPanel from '@/views/system/dict/components/DictDataSearchPanel.vue'

describe('dictionary data page controls', () => {
  it('does not render import or export actions for dictionary data', () => {
    const wrapper = mount(DictionaryPageHeader, {
      props: {
        kind: 'data',
        total: '共 0 条',
        refreshLoading: false,
      },
      global: {
        directives: {
          permission: () => undefined,
        },
      },
    })

    expect(wrapper.text()).not.toContain('导入字典')
    expect(wrapper.text()).not.toContain('导出字典')
  })

  it('requires a concrete dictionary type without an all-types option', () => {
    const wrapper = mount(DictDataSearchPanel, {
      props: {
        model: { dict_type: null, status: null },
        initialValues: { dict_type: null, status: null },
        loading: false,
        dictTypes: [
          {
            dict_id: 1,
            dict_name: '用户性别',
            dict_type: 'sys_user_sex',
            status: '1',
            remark: null,
            create_time: '2026-08-10T09:00:00+08:00',
            update_time: '2026-08-10T09:00:00+08:00',
          },
        ],
      },
      global: {
        stubs: {
          AppSearchForm: {
            name: 'AppSearchForm',
            props: ['fields'],
            template: '<div />',
          },
        },
      },
    })
    const searchForm = wrapper.findComponent({ name: 'AppSearchForm' })
    const fields = searchForm.props('fields')

    expect(fields).toEqual(
      expect.arrayContaining([
        expect.objectContaining({
          key: 'dict_type',
          required: true,
          componentProps: expect.objectContaining({
            clearable: false,
            options: [{ label: '用户性别', value: 'sys_user_sex' }],
          }),
        }),
      ]),
    )
  })
})
