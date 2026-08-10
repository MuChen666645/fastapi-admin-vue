import { flushPromises, mount } from '@vue/test-utils'
import { reactive, h } from 'vue'
import { describe, expect, it } from 'vitest'
import { NTreeSelect } from 'naive-ui'

import AppForm from '../components/AppForm/index.vue'
import type { AppFormField, AppFormGroup } from '../types'

interface TestFormModel {
  name: string
  members: Array<{ name: string }>
  description: string
}

const createModel = (): TestFormModel => ({
  name: '',
  members: [],
  description: '',
})

describe('AppForm', () => {
  it('validates before emitting submit and supports reset', async () => {
    const model = reactive(createModel())
    const fields: AppFormField[] = [{ key: 'name', path: 'name', label: '名称', required: true }]
    const wrapper = mount(AppForm, {
      props: {
        model,
        fields,
        initialValues: model,
      },
    })
    const submitForm = async (): Promise<void> => {
      await wrapper.get('form').trigger('submit')
      await flushPromises()
    }

    await submitForm()

    expect(wrapper.emitted('submit')).toBeUndefined()
    const validationEvents = wrapper.emitted('validate') ?? []
    expect(validationEvents[validationEvents.length - 1]?.[0]).toMatchObject({ valid: false })

    await wrapper.get('[data-testid="app-form-field-name"] input').setValue('管理员')
    await submitForm()

    expect(wrapper.emitted('submit')).toHaveLength(1)
    expect(model.name).toBe('管理员')

    await wrapper.get('.app-form__reset').trigger('click')
    expect(model.name).toBe('')

    wrapper.unmount()
  })

  it('adds, validates, and removes repeated groups', async () => {
    const model = reactive(createModel())
    const groups: AppFormGroup[] = [
      {
        key: 'members',
        path: 'members',
        title: '成员',
        fields: [{ key: 'name', path: 'name', label: '姓名', required: true }],
        createItem: () => ({ name: '' }),
        emptyText: '暂无成员',
      },
    ]
    const wrapper = mount(AppForm, { props: { model, groups } })

    expect(wrapper.get('.n-empty').text()).toContain('暂无成员')
    await wrapper.get('.app-form-group__add').trigger('click')
    expect(model.members).toHaveLength(1)

    const submitForm = async (): Promise<void> => {
      await wrapper.get('form').trigger('submit')
      await flushPromises()
    }

    await submitForm()
    expect(wrapper.emitted('submit')).toBeUndefined()

    await wrapper.get('[data-testid="app-form-field-members-0-name"] input').setValue('管理员')
    await submitForm()
    expect(wrapper.emitted('submit')).toHaveLength(1)

    await wrapper.get('.app-form-group__remove').trigger('click')
    expect(model.members).toHaveLength(0)
    expect(wrapper.emitted('group-remove')).toHaveLength(1)

    wrapper.unmount()
  })

  it('allows a custom field slot to use the same model contract', async () => {
    const model = reactive(createModel())
    const fields: AppFormField[] = [
      { key: 'description', path: 'description', label: '描述', type: 'custom' },
    ]
    const wrapper = mount(AppForm, {
      props: { model, fields },
      slots: {
        'field-description': (slotProps: { value: unknown; setValue: (value: unknown) => void }) =>
          h('textarea', {
            'data-testid': 'custom-description',
            value: typeof slotProps.value === 'string' ? slotProps.value : '',
            onInput: (event: Event) => {
              const target = event.target
              if (target instanceof HTMLTextAreaElement) {
                slotProps.setValue(target.value)
              }
            },
          }),
      },
    })

    await wrapper.get('[data-testid="custom-description"]').setValue('自定义内容')
    expect(model.description).toBe('自定义内容')

    wrapper.unmount()
  })

  it('supports tree-select fields and transforms cleared values', async () => {
    const model = reactive({ departments: [] as number[] })
    const fields: AppFormField[] = [
      {
        key: 'departments',
        path: 'departments',
        label: 'Departments',
        type: 'tree-select',
        componentProps: {
          multiple: true,
          options: [{ key: 1, label: 'Headquarters' }],
        },
        valueTransform: (value) =>
          Array.isArray(value) ? value.filter((key): key is number => typeof key === 'number') : [],
      },
    ]
    const wrapper = mount(AppForm, { props: { model, fields } })
    const treeSelect = wrapper.findComponent(NTreeSelect)

    expect(treeSelect.exists()).toBe(true)

    treeSelect.vm.$emit('update:value', [1])
    await flushPromises()
    expect(model.departments).toEqual([1])

    treeSelect.vm.$emit('update:value', null)
    await flushPromises()
    expect(model.departments).toEqual([])

    wrapper.unmount()
  })
})
