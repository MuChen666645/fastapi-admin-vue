import { flushPromises, mount } from '@vue/test-utils'
import { NMessageProvider } from 'naive-ui'
import { createPinia } from 'pinia'
import { defineComponent } from 'vue'
import { describe, expect, it, vi } from 'vitest'

import SearchFormDemoView from '../views/demo/search-form/index.vue'

const TestHost = defineComponent({
  components: {
    NMessageProvider,
    SearchFormDemoView,
  },
  template: '<NMessageProvider><SearchFormDemoView /></NMessageProvider>',
})

describe('SearchFormDemoView', () => {
  it('filters local records and expands advanced conditions', async () => {
    vi.useFakeTimers()
    const wrapper = mount(TestHost, {
      global: {
        plugins: [createPinia()],
      },
    })

    try {
      expect(wrapper.find('main.search-form-demo-page').exists()).toBe(true)
      expect(wrapper.get('h1').text()).toBe('标准搜索表单')
      expect(wrapper.text()).toContain('常用条件优先展示，高级条件可折叠')
      expect(wrapper.find('[data-testid="app-form-field-category"]').exists()).toBe(false)

      await wrapper.get('[data-testid="app-form-field-keyword"] input').setValue('权限')
      await wrapper.get('.search-form-demo-search-button').trigger('click')
      await flushPromises()
      vi.advanceTimersByTime(350)
      await flushPromises()

      expect(wrapper.findAll('.search-form-demo-record')).toHaveLength(1)
      expect(wrapper.text()).toContain('用户权限中心')

      await wrapper.get('.search-form-demo-toggle').trigger('click')
      expect(wrapper.find('[data-testid="app-form-field-category"]').exists()).toBe(true)
    } finally {
      wrapper.unmount()
      vi.useRealTimers()
    }
  })
})
