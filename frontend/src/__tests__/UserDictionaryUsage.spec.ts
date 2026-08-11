import { defineComponent, h, isVNode } from 'vue'
import { mount } from '@vue/test-utils'
import type { DataTableColumns } from 'naive-ui'
import { describe, expect, it } from 'vitest'

import DictTag from '@/components/DictTag/index.vue'
import UserFormModal from '@/views/system/user/components/UserFormModal.vue'
import UserTable from '@/views/system/user/components/UserTable.vue'
import type { AppFormField, UserFormModel, UserListItem } from '@/types'
import { toUserSexSelectOptions } from '@/utils'

const dictionary = [
  {
    dict_code: 1000,
    dict_sort: 1,
    dict_label: 'Female',
    dict_value: '0',
    dict_type: 'sys_user_sex',
    status: '1' as const,
    remark: null,
    create_time: '2026-08-10T09:00:00+08:00',
    update_time: '2026-08-10T10:00:00+08:00',
  },
  {
    dict_code: 1001,
    dict_sort: 2,
    dict_label: 'Male',
    dict_value: '1',
    dict_type: 'sys_user_sex',
    status: '1' as const,
    remark: null,
    create_time: '2026-08-10T09:00:00+08:00',
    update_time: '2026-08-10T10:00:00+08:00',
  },
  {
    dict_code: 1002,
    dict_sort: 3,
    dict_label: 'Unknown',
    dict_value: '2',
    dict_type: 'sys_user_sex',
    status: '1' as const,
    remark: null,
    create_time: '2026-08-10T09:00:00+08:00',
    update_time: '2026-08-10T10:00:00+08:00',
  },
]

const model: UserFormModel = {
  username: '',
  password: '',
  phone: '',
  email: '',
  nickname: '',
  sex: null,
  status: '1',
  dept_id: null,
  post_ids: [],
  role_ids: [],
  version: null,
}

const user: UserListItem = {
  id: 7,
  create_time: '2026-08-10T09:00:00+08:00',
  username: 'alice',
  email: null,
  phone: null,
  role_id: 2,
  dept_id: null,
  nickname: 'Alice',
  sex: '0',
  avatar: null,
  update_time: null,
  status: '1',
  version: 1,
}

const AppFormStub = defineComponent({
  name: 'AppForm',
  props: { fields: { type: Array, required: true } },
  setup: () => () => h('div'),
})

const NModalStub = defineComponent({
  name: 'NModal',
  setup:
    (_props, { slots }) =>
    () =>
      h('div', slots.default?.()),
})

const NDataTableStub = defineComponent({
  name: 'NDataTable',
  props: { columns: { type: Array, required: true } },
  setup: () => () => h('div'),
})

describe('user dictionary usage', () => {
  it('converts backend sex data to form options and ignores unsupported values', () => {
    expect(toUserSexSelectOptions(dictionary)).toEqual([
      { label: 'Female', value: '0' },
      { label: 'Male', value: '1' },
    ])
  })

  it('uses dictionary labels in the user form', () => {
    const wrapper = mount(UserFormModal, {
      props: {
        show: true,
        mode: 'create',
        model,
        loading: false,
        departments: [],
        posts: [],
        roles: [],
        sexOptions: dictionary,
      },
      global: {
        stubs: { AppForm: AppFormStub, Modal: NModalStub, Button: true, Icon: true },
        directives: { permission: () => undefined },
      },
    })

    const fields = wrapper
      .findComponent(AppFormStub)
      .props('fields') as AppFormField<UserFormModel>[]
    const sexField = fields.find((field) => field.key === 'sex')
    expect(
      sexField && typeof sexField.componentProps === 'object' ? sexField.componentProps : null,
    ).toMatchObject({
      options: [
        { label: 'Female', value: '0' },
        { label: 'Male', value: '1' },
      ],
    })
  })

  it('renders the user list sex column with DictTag', () => {
    const wrapper = mount(UserTable, {
      props: {
        data: [user],
        loading: false,
        departmentNames: {},
        sexOptions: dictionary,
        selectedRowKeys: [],
      },
      global: { stubs: { DataTable: NDataTableStub } },
    })

    const columns = wrapper
      .findComponent(NDataTableStub)
      .props('columns') as DataTableColumns<UserListItem>
    const sexColumn = columns.find((column) => 'key' in column && column.key === 'sex')
    if (!sexColumn || !('render' in sexColumn) || !sexColumn.render) {
      throw new Error('User sex column is missing')
    }

    const rendered = sexColumn.render(user, 0)
    expect(isVNode(rendered)).toBe(true)
    if (!isVNode(rendered)) {
      return
    }

    expect(rendered.type).toBe(DictTag)
    expect(rendered.props).toMatchObject({ options: dictionary, value: '0' })
  })
})
