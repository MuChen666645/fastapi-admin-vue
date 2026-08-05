import { flushPromises, mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import AppSearchForm from '../components/AppSearchForm/index.vue'
import UtilsDemoView from '../views/demo/utils/index.vue'

describe('UtilsDemoView', () => {
  it('runs the moment utility demo with the default input', async () => {
    const wrapper = mount(UtilsDemoView)

    expect(wrapper.find('main.utils-demo-page').exists()).toBe(true)
    expect(wrapper.findComponent(AppSearchForm).exists()).toBe(true)
    expect(wrapper.get('h1').text()).toBe('工具函数')
    expect(wrapper.text()).toContain('解析成功')
    expect(wrapper.text()).toContain('2026-08-05 13:14:15')
    expect(wrapper.text()).toContain('zh-cn')

    await wrapper.get('input').setValue('2025-02-29 13:14:15')
    await wrapper.get('.app-search-form__submit').trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('解析失败')
    expect(wrapper.text()).toContain('无法解析')
  })
})
