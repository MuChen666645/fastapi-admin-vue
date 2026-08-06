import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import UtilsDemoView from '../views/demo/utils/index.vue'

describe('UtilsDemoView', () => {
  it('runs the moment utility demo with the default input', async () => {
    const wrapper = mount(UtilsDemoView)

    expect(wrapper.find('main.utils-demo-page').exists()).toBe(true)
    expect(wrapper.find('.utils-demo-header').exists()).toBe(false)
    expect(wrapper.text()).toContain('解析成功')
    expect(wrapper.text()).toContain('2026-08-05 13:14:15')
    expect(wrapper.text()).toContain('zh-cn')

    await wrapper.get('input').setValue('2025-02-29 13:14:15')
    await wrapper.get('.utils-demo-run').trigger('click')

    expect(wrapper.text()).toContain('解析失败')
    expect(wrapper.text()).toContain('无法解析')
  })
})
