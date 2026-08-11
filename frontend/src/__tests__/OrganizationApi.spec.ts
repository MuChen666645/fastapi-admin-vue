import { beforeEach, describe, expect, it, vi } from 'vitest'

const requestJson = vi.hoisted(() => vi.fn())

vi.mock('../utils/request', () => ({ requestJson }))

import {
  createDepartment,
  deleteDepartment,
  fetchDepartmentDetail,
  fetchDepartmentList,
  updateDepartment,
} from '@/api/organization'
import {
  parseDepartmentDetail,
  parseDepartmentOptions,
  parseDepartmentTree,
} from '@/api/organization/parsers'

const department = {
  dept_id: 2,
  parent_id: 1,
  ancestors: '0,1',
  dept_name: '研发部',
  order_num: 2,
  leader: 'Alice',
  phone: '010-12345678',
  email: 'alice@example.com',
  status: '1',
  create_time: '2026-08-10T09:00:00+08:00',
  update_time: '2026-08-10T10:00:00+08:00',
  children: [],
}

describe('部门 API', () => {
  beforeEach(() => {
    requestJson.mockReset()
    requestJson.mockResolvedValue(null)
  })

  it('按后端契约查询部门树和部门详情', async () => {
    await fetchDepartmentList({ name: ' 研发 ', status: '1' })
    await fetchDepartmentDetail(2)

    expect(requestJson).toHaveBeenNthCalledWith(
      1,
      '/dept/list',
      { params: { name: '研发', status: '1' } },
      expect.any(Function),
    )
    expect(requestJson).toHaveBeenNthCalledWith(2, '/dept/2', {}, expect.any(Function))
  })

  it('使用真实方法和路径新增、修改及删除部门', async () => {
    const payload = {
      parent_id: null,
      dept_name: '研发部',
      order_num: 2,
      leader: null,
      phone: null,
      email: null,
      status: '1' as const,
    }

    await createDepartment(payload)
    await updateDepartment(2, payload)
    await deleteDepartment(2)

    expect(requestJson).toHaveBeenNthCalledWith(
      1,
      '/dept/add',
      { method: 'POST', data: payload },
      expect.any(Function),
    )
    expect(requestJson).toHaveBeenNthCalledWith(
      2,
      '/dept/2',
      { method: 'PUT', data: payload },
      expect.any(Function),
    )
    expect(requestJson).toHaveBeenNthCalledWith(
      3,
      '/dept/2',
      { method: 'DELETE' },
      expect.any(Function),
    )
  })

  it('严格解析部门树、详情和精简选项', () => {
    expect(parseDepartmentTree([department])).toEqual([department])
    expect(parseDepartmentDetail(department)).toEqual({
      dept_id: 2,
      parent_id: 1,
      ancestors: '0,1',
      dept_name: '研发部',
      order_num: 2,
      leader: 'Alice',
      phone: '010-12345678',
      email: 'alice@example.com',
      status: '1',
      create_time: '2026-08-10T09:00:00+08:00',
      update_time: '2026-08-10T10:00:00+08:00',
    })
    expect(parseDepartmentOptions([department])).toEqual([
      { dept_id: 2, dept_name: '研发部', status: '1', children: [] },
    ])
  })

  it('拒绝字段缺失和非法状态的部门响应', () => {
    expect(() => parseDepartmentTree([{ ...department, children: undefined }])).toThrow(
      '部门树数据无效',
    )
    expect(() => parseDepartmentTree([{ ...department, status: 'enabled' }])).toThrow(
      '接口字段 status 无效',
    )
  })
})
