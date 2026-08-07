import { beforeEach, describe, expect, it, vi } from 'vitest'

const requestJson = vi.hoisted(() => vi.fn())
const requestBlob = vi.hoisted(() => vi.fn())

vi.mock('../utils/request', () => ({ requestBlob, requestJson }))

import {
  batchDeleteUsers,
  batchUpdateUserStatus,
  bindUserRoles,
  deleteUser,
  exportUsers,
  fetchUserList,
  importUsers,
  resetUserPassword,
  updateUser,
} from '@/api/user'
import { parseUserDetail, parseUserImportResult, parseUserListPage } from '@/api/user/parsers'
import type { UserListFilters } from '@/types'

const listResponse = {
  items: [
    {
      id: 7,
      create_time: '2026-08-05T09:00:00+08:00',
      username: 'alice',
      email: null,
      phone: null,
      role_id: 2,
      dept_id: 3,
      nickname: 'Alice',
      sex: '1',
      avatar: null,
      update_time: null,
      status: '1',
      version: 2,
    },
  ],
  total: 1,
  page: 2,
  size: 20,
  pages: 1,
}

const filters: UserListFilters = {
  username: ' alice ',
  nickname: 'Alice',
  phone: '',
  email: 'example.com',
  create_time: null,
}

describe('用户 API', () => {
  beforeEach(() => {
    requestBlob.mockReset()
    requestJson.mockReset()
  })

  it('调用用户导出接口并保留文件响应', async () => {
    const fileResponse = { blob: new Blob(['users']), filename: 'users.xlsx' }
    requestBlob.mockResolvedValueOnce(fileResponse)

    await expect(exportUsers()).resolves.toBe(fileResponse)

    expect(requestBlob).toHaveBeenCalledWith('/user/export', {})
  })

  it('使用 file 字段上传用户导入文件并解析结果', async () => {
    requestJson.mockResolvedValueOnce({ imported: 1, failed: 0, errors: [] })
    const file = new File(['users'], 'users.xlsx')

    await expect(importUsers(file)).resolves.toEqual({ imported: 1, failed: 0, errors: [] })

    const [, options] = requestJson.mock.calls[0] as [string, { data: FormData }]
    const uploadedFile = options.data.get('file')
    expect(uploadedFile).toBeInstanceOf(File)
    expect((uploadedFile as File).name).toBe('users.xlsx')
    await expect((uploadedFile as File).text()).resolves.toBe('users')
    expect(parseUserImportResult({ imported: 1, failed: 0, errors: [] })).toEqual({
      imported: 1,
      failed: 0,
      errors: [],
    })
  })

  it('调用用户批量状态和批量删除接口', async () => {
    requestJson.mockResolvedValue(null)

    await batchUpdateUserStatus({ user_ids: [7, 8], status: '0' })
    await batchDeleteUsers({ user_ids: [7, 8] })

    expect(requestJson).toHaveBeenNthCalledWith(
      1,
      '/user/batch/status',
      { method: 'PUT', data: { user_ids: [7, 8], status: '0' } },
      expect.any(Function),
    )
    expect(requestJson).toHaveBeenNthCalledWith(
      2,
      '/user/batch',
      { method: 'DELETE', data: { user_ids: [7, 8] } },
      expect.any(Function),
    )
  })

  it('按后端契约序列化用户列表筛选条件', async () => {
    requestJson.mockResolvedValueOnce(listResponse)

    await fetchUserList({ page: 2, size: 20 }, filters)

    expect(requestJson).toHaveBeenCalledWith(
      '/user/list',
      {
        params: {
          page: 2,
          size: 20,
          username: 'alice',
          nickname: 'Alice',
          email: 'example.com',
        },
      },
      expect.any(Function),
    )
  })

  it('接受字段权限脱敏后的空值并解析用户详情关联数据', () => {
    expect(parseUserListPage(listResponse).items[0]).toMatchObject({
      id: 7,
      email: null,
      phone: null,
      version: 2,
    })

    const detail = parseUserDetail({
      user: listResponse.items[0],
      roles: [
        {
          id: 2,
          name: '运营',
          code: 'operator',
          description: null,
          status: '1',
        },
      ],
      posts: [
        {
          post_id: 4,
          post_code: 'support',
          post_name: '客服',
          status: '1',
        },
      ],
      permissions: ['system:user:edit'],
    })

    expect(detail.roles[0]?.id).toBe(2)
    expect(detail.posts[0]?.post_id).toBe(4)
  })

  it('使用用户维护接口的真实方法和请求体', async () => {
    requestJson.mockResolvedValue(null)

    await updateUser(7, { username: 'alice', version: 2, status: '1' })
    await bindUserRoles(7, { role_ids: [2] })
    await resetUserPassword(7, { password: 'new-password' })
    await deleteUser(7)

    expect(requestJson).toHaveBeenNthCalledWith(
      1,
      '/user/7',
      { method: 'PUT', data: { username: 'alice', version: 2, status: '1' } },
      expect.any(Function),
    )
    expect(requestJson).toHaveBeenNthCalledWith(
      2,
      '/user/7/roles',
      { method: 'PUT', data: { role_ids: [2] } },
      expect.any(Function),
    )
    expect(requestJson).toHaveBeenNthCalledWith(
      3,
      '/user/7/reset-password',
      { method: 'PUT', data: { password: 'new-password' } },
      expect.any(Function),
    )
    expect(requestJson).toHaveBeenNthCalledWith(
      4,
      '/user/7',
      { method: 'DELETE' },
      expect.any(Function),
    )
  })

  it('拒绝缺少用户列表必要字段的响应', () => {
    expect(() => parseUserListPage({ ...listResponse, items: [{ id: 7 }] })).toThrow(
      '接口字段 create_time 无效',
    )
  })
})
