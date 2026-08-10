import { describe, expect, it } from 'vitest'

import type { RoleFormModel } from '@/types'
import { createRolePayload, createRoleUpdatePayload } from '@/views/system/role/payloads'

const createFormModel = (): RoleFormModel => ({
  name: ' 运维角色 ',
  code: ' operator ',
  description: ' 查看敏感字段 ',
  data_scope: '2',
  status: '1',
  menu_ids: [4, 5],
  dept_ids: [7],
  field_permission_codes: ['field:user:email', 'field:user:phone'],
  version: 3,
})

describe('角色表单请求体', () => {
  it('创建时同步字段权限编码', () => {
    expect(createRolePayload(createFormModel())).toMatchObject({
      field_permission_codes: ['field:user:email', 'field:user:phone'],
    })
  })

  it('编辑保存时同步字段权限编码', () => {
    expect(createRoleUpdatePayload(createFormModel())).toEqual({
      name: '运维角色',
      description: '查看敏感字段',
      data_scope: '2',
      status: '1',
      version: 3,
      menu_ids: [4, 5],
      dept_ids: [7],
      field_permission_codes: ['field:user:email', 'field:user:phone'],
    })
  })
})
