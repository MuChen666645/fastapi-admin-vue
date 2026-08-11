import { describe, expect, it } from 'vitest'

import type { DepartmentFormModel, DepartmentListItem } from '@/types'
import { createDepartmentParentOptions } from '@/views/system/dept/options'
import {
  createDepartmentPayload,
  createDepartmentUpdatePayload,
} from '@/views/system/dept/payloads'

const model: DepartmentFormModel = {
  parent_id: 0,
  dept_name: ' 研发部 ',
  order_num: 3,
  leader: ' Alice ',
  phone: ' ',
  email: ' alice@example.com ',
  status: '1',
}

const departments: DepartmentListItem[] = [
  {
    dept_id: 1,
    parent_id: null,
    ancestors: '0',
    dept_name: '总部',
    order_num: 1,
    leader: null,
    phone: null,
    email: null,
    status: '1',
    create_time: '2026-08-10T09:00:00+08:00',
    update_time: '2026-08-10T10:00:00+08:00',
    children: [
      {
        dept_id: 2,
        parent_id: 1,
        ancestors: '0,1',
        dept_name: '研发部',
        order_num: 1,
        leader: null,
        phone: null,
        email: null,
        status: '1',
        create_time: '2026-08-10T09:00:00+08:00',
        update_time: '2026-08-10T10:00:00+08:00',
        children: [
          {
            dept_id: 3,
            parent_id: 2,
            ancestors: '0,1,2',
            dept_name: '平台组',
            order_num: 1,
            leader: null,
            phone: null,
            email: null,
            status: '1',
            create_time: '2026-08-10T09:00:00+08:00',
            update_time: '2026-08-10T10:00:00+08:00',
            children: [],
          },
        ],
      },
    ],
  },
]

describe('部门载荷与父级选项', () => {
  it('将顶级部门和空文本转换为后端 DTO', () => {
    expect(createDepartmentPayload(model)).toEqual({
      parent_id: null,
      dept_name: '研发部',
      order_num: 3,
      leader: 'Alice',
      phone: null,
      email: 'alice@example.com',
      status: '1',
    })
    expect(createDepartmentUpdatePayload(model)).toEqual(createDepartmentPayload(model))
  })

  it('编辑部门时禁选自身和全部后代', () => {
    expect(createDepartmentParentOptions(departments, 2, '顶级部门')).toEqual([
      { key: 0, label: '顶级部门' },
      {
        key: 1,
        label: '总部',
        children: [
          {
            key: 2,
            label: '研发部',
            disabled: true,
            children: [{ key: 3, label: '平台组', disabled: true }],
          },
        ],
      },
    ])
  })
})
