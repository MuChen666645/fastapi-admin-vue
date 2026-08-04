import { flushPromises, mount } from '@vue/test-utils'
import { NMessageProvider } from 'naive-ui'
import { createPinia } from 'pinia'
import { defineComponent } from 'vue'
import { describe, expect, it, vi } from 'vitest'

import FormDemoView from '../views/demo/form/index.vue'

const TestHost = defineComponent({
  components: {
    FormDemoView,
    NMessageProvider,
  },
  template: '<NMessageProvider><FormDemoView /></NMessageProvider>',
})

describe('FormDemoView', () => {
  it('renders the complete form demo and supports adding reviewer groups', async () => {
    const wrapper = mount(TestHost, {
      global: {
        plugins: [createPinia()],
      },
    })

    expect(wrapper.find('main.form-demo-page').exists()).toBe(true)
    expect(wrapper.get('h1').text()).toBe('标准提交表单')
    expect(wrapper.text()).toContain('自定义备注控件和字段插槽')
    expect(wrapper.text()).toContain('评审成员分组的新增、删除和数量限制')
    expect(wrapper.find('[data-testid="app-form-field-remarks"] textarea').exists()).toBe(true)
    expect(wrapper.findAll('[data-testid^="app-form-group-item-reviewers-"]')).toHaveLength(1)

    await wrapper.get('.app-form-group__add').trigger('click')

    expect(wrapper.findAll('[data-testid^="app-form-group-item-reviewers-"]')).toHaveLength(2)

    wrapper.unmount()
  })

  it('completes a valid submit without leaking reactive proxies to the result preview', async () => {
    vi.useFakeTimers()
    const wrapper = mount(TestHost, {
      global: {
        plugins: [createPinia()],
      },
    })

    await wrapper.get('form').trigger('submit')
    await flushPromises()
    vi.advanceTimersByTime(450)
    await flushPromises()

    expect(wrapper.find('.form-demo-result').exists()).toBe(true)
    expect(wrapper.find('.form-demo-result pre').text()).toContain('组件规范升级')

    wrapper.unmount()
    vi.useRealTimers()
  })
})
