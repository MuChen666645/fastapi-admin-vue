import { flushPromises, mount } from '@vue/test-utils'
import { NDataTable } from 'naive-ui'
import { describe, expect, it, vi } from 'vitest'

import AppSearchForm from '../components/AppSearchForm/index.vue'
import HooksDemoView from '../views/demo/hooks/index.vue'

describe('HooksDemoView', () => {
  it('uses the shared search form and data table pagination', async () => {
    vi.useFakeTimers()
    const wrapper = mount(HooksDemoView)

    try {
      await vi.advanceTimersByTimeAsync(280)
      await flushPromises()

      expect(wrapper.find('main.hooks-demo-page').exists()).toBe(true)
      expect(wrapper.findComponent(AppSearchForm).exists()).toBe(true)
      const table = wrapper.findComponent(NDataTable)
      expect(table.props('remote')).toBe(true)
      expect(table.props('pagination')).not.toBe(false)
      expect(wrapper.find('.hooks-demo-header').exists()).toBe(false)
      expect(wrapper.text()).toContain('共 15 条记录')
      expect(wrapper.text()).toContain('usePagination')

      await wrapper.get('[data-testid="app-form-field-keyword"] input').setValue('useTheme')
      await wrapper.get('.app-search-form__submit').trigger('click')
      await vi.advanceTimersByTimeAsync(280)
      await flushPromises()

      expect(wrapper.text()).toContain('共 1 条记录')
      expect(wrapper.text()).toContain('useTheme')
    } finally {
      wrapper.unmount()
      vi.useRealTimers()
    }
  })
})
