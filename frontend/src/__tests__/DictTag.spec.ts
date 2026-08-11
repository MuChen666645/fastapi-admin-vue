import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import DictTag from '@/components/DictTag/index.vue'

const options = [
  {
    dict_code: 2,
    dict_sort: 1,
    dict_label: '男',
    dict_value: '0',
    dict_type: 'sys_user_sex',
    status: '1' as const,
    remark: null,
    create_time: '2026-08-10T09:00:00+08:00',
    update_time: '2026-08-10T10:00:00+08:00',
  },
  {
    dict_code: 3,
    dict_sort: 2,
    dict_label: '女',
    dict_value: '1',
    dict_type: 'sys_user_sex',
    status: '1' as const,
    remark: null,
    create_time: '2026-08-10T09:00:00+08:00',
    update_time: '2026-08-10T10:00:00+08:00',
  },
]

describe('DictTag', () => {
  it('按字典值渲染一个或多个标签', () => {
    const wrapper = mount(DictTag, { props: { options, value: ['0', 1], type: 'success' } })

    expect(wrapper.text()).toContain('男')
    expect(wrapper.text()).toContain('女')
    expect(wrapper.findAll('.n-tag')).toHaveLength(2)
  })

  it('默认显示未匹配值并允许隐藏', async () => {
    const wrapper = mount(DictTag, { props: { options, value: 'unknown' } })

    expect(wrapper.text()).toBe('unknown')
    await wrapper.setProps({ showValue: false })
    expect(wrapper.html()).toBe('<!--v-if-->')
  })
})
