import { beforeEach, describe, expect, it, vi } from 'vitest'

const requestJson = vi.hoisted(() => vi.fn())
const requestBlob = vi.hoisted(() => vi.fn())

vi.mock('../utils/request', () => ({ requestBlob, requestJson }))

import {
  batchUpdateRoleStatus,
  createRole,
  deleteRole,
  exportRoles,
  fetchRoleDetail,
  fetchRoleList,
  importRoles,
  updateRole,
} from '@/api/role'
import { parseMenuList } from '@/api/menu/parsers'
import { parseRoleDetail, parseRoleImportResult, parseRolePage } from '@/api/role/parsers'
import type { RoleListFilters } from '@/types'

const filters: RoleListFilters = { name: ' 运维 ', code: ' operator ' }

const role = {
  id: 2,
  name: '运维',
  code: 'operator',
  description: '运维角色',
  data_scope: '5',
  status: '1',
  version: 3,
  create_time: '2026-08-07T09:00:00+08:00',
  update_time: '2026-08-07T10:00:00+08:00',
}

describe('角色 API', () => {
  beforeEach(() => {
    requestJson.mockReset()
    requestBlob.mockReset()
  })

  it('按后端契约查询角色分页', async () => {
    requestJson.mockResolvedValueOnce(
      parseRolePage({ items: [role], total: 1, page: 1, size: 20, pages: 1 }),
    )

    await fetchRoleList({ page: 1, size: 20 }, filters)

    expect(requestJson).toHaveBeenCalledWith(
      '/role/list',
      { params: { page: 1, size: 20, name: '运维', code: 'operator' } },
      expect.any(Function),
    )
  })

  it('调用角色详情、写入、删除、批量状态和文件接口', async () => {
    requestJson.mockResolvedValue(null)
    requestBlob.mockResolvedValue({ blob: new Blob(['roles']), filename: 'roles.xlsx' })

    await fetchRoleDetail(2)
    await createRole({
      name: '运维',
      code: 'operator',
      description: null,
      data_scope: '5',
      menu_ids: [],
      dept_ids: [],
      field_permission_codes: [],
    })
    await updateRole(2, {
      version: 3,
      status: '0',
      field_permission_codes: ['field:user:email'],
    })
    await batchUpdateRoleStatus({ role_ids: [2], status: '1' })
    await deleteRole(2)
    await exportRoles()
    await importRoles(new File(['roles'], 'roles.xlsx'))

    expect(requestJson).toHaveBeenNthCalledWith(1, '/role/2', {}, expect.any(Function))
    expect(requestJson).toHaveBeenNthCalledWith(
      2,
      '/role/add',
      expect.objectContaining({ method: 'POST' }),
      expect.any(Function),
    )
    expect(requestJson).toHaveBeenNthCalledWith(
      3,
      '/role/2',
      {
        method: 'PUT',
        data: {
          version: 3,
          status: '0',
          field_permission_codes: ['field:user:email'],
        },
      },
      expect.any(Function),
    )
    expect(requestJson).toHaveBeenNthCalledWith(
      4,
      '/role/batch/status',
      { method: 'PUT', data: { role_ids: [2], status: '1' } },
      expect.any(Function),
    )
    expect(requestJson).toHaveBeenNthCalledWith(
      5,
      '/role/2',
      { method: 'DELETE' },
      expect.any(Function),
    )
    expect(requestBlob).toHaveBeenCalledWith('/role/export', {})

    const [, importOptions] = requestJson.mock.calls[5] as [string, { data: FormData }]
    expect(importOptions.data.get('file')).toBeInstanceOf(File)
  })

  it('解析角色详情、菜单树和导入结果', () => {
    expect(
      parseRoleDetail({
        ...role,
        menu_ids: [4],
        dept_ids: [7],
        field_permission_codes: ['field:user:email'],
      }),
    ).toMatchObject({
      id: 2,
      menu_ids: [4],
      dept_ids: [7],
      field_permission_codes: ['field:user:email'],
    })
    expect(
      parseMenuList([
        {
          menu_id: 4,
          menu_name: '角色管理',
          menu_path: '/system/role',
          parent_id: null,
          perms: 'system:role:list',
          sort: 1,
          menu_type: 'C',
          link_url: null,
          icon: 'ShieldOutline',
          component: 'system/role/index',
          is_cache: '0',
          is_hidden: '0',
          create_time: role.create_time,
          status: '1',
          update_time: role.update_time,
          remark: null,
          children: [],
        },
      ]),
    ).toMatchObject([{ menu_id: 4, children: [] }])
    expect(
      parseRoleImportResult({ imported: 2, failed: 1, errors: [{ row: 3, message: '编码重复' }] }),
    ).toEqual({
      imported: 2,
      failed: 1,
      errors: [{ row: 3, message: '编码重复' }],
    })
  })
})
