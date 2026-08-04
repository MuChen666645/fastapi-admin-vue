import { flushPromises, mount } from '@vue/test-utils'
import { h, reactive } from 'vue'
import { describe, expect, it } from 'vitest'

import AppSearchForm from '../components/AppSearchForm/index.vue'
import type { AppFormField } from '../types'

interface TestSearchModel {
  [key: string]: unknown
  keyword: string
  status: string
  owner: string
}

const createModel = (): TestSearchModel => ({
  keyword: '',
  status: 'all',
  owner: '',
})

describe('AppSearchForm', () => {
  it('supports collapsed fields, custom controls, validation, search, and reset', async () => {
    const model = reactive(createModel())
    const fields: AppFormField[] = [
      { key: 'keyword', path: 'keyword', label: '关键词', required: true },
      { key: 'status', path: 'status', label: '状态', type: 'select' },
      { key: 'owner', path: 'owner', label: '负责人' },
    ]
    const wrapper = mount(AppSearchForm, {
      props: {
        model,
        fields,
        defaultCollapsed: true,
        collapsedFields: 1,
        initialValues: model,
      },
      slots: {
        'field-keyword': (slotProps: { value: unknown; setValue: (value: unknown) => void }) =>
          h('input', {
            'data-testid': 'custom-keyword',
            value: typeof slotProps.value === 'string' ? slotProps.value : '',
            onInput: (event: Event) => {
              const target = event.target
              if (target instanceof HTMLInputElement) {
                slotProps.setValue(target.value)
              }
            },
          }),
      },
    })

    expect(wrapper.find('[data-testid="custom-keyword"]').exists()).toBe(true)
    expect(wrapper.find('[data-testid="app-form-field-status"]').exists()).toBe(false)

    await wrapper.get('form').trigger('submit')
    await flushPromises()
    expect(wrapper.emitted('search')).toBeUndefined()
    expect(wrapper.emitted('validate')?.slice(-1)[0]?.[0]).toMatchObject({ valid: false })

    await wrapper.get('[data-testid="custom-keyword"]').setValue('管理员')
    await wrapper.get('form').trigger('submit')
    await flushPromises()

    expect(wrapper.emitted('search')).toHaveLength(1)
    expect(model.keyword).toBe('管理员')

    await wrapper.get('.app-search-form__toggle').trigger('click')
    expect(wrapper.find('[data-testid="app-form-field-status"]').exists()).toBe(true)

    await wrapper.get('.app-search-form__reset').trigger('click')
    expect(model.keyword).toBe('')
    expect(wrapper.emitted('reset')).toHaveLength(1)

    wrapper.unmount()
  })

  it('does not emit search for Enter when searchOnEnter is disabled', async () => {
    const model = reactive(createModel())
    const fields: AppFormField[] = [{ key: 'keyword', path: 'keyword', label: '关键词' }]
    const wrapper = mount(AppSearchForm, {
      props: { model, fields, searchOnEnter: false },
    })

    await wrapper.get('[data-testid="app-form-field-keyword"] input').setValue('管理员')
    await wrapper.get('form').trigger('submit')
    await flushPromises()

    expect(wrapper.emitted('search')).toBeUndefined()

    wrapper.unmount()
  })
})
