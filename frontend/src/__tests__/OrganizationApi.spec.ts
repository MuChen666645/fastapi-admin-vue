import { beforeEach, describe, expect, it, vi } from 'vitest'

const requestJson = vi.hoisted(() => vi.fn())

vi.mock('../utils/request', () => ({ requestJson }))

import {
  createDepartment,
  createPost,
  deleteDepartment,
  deletePost,
  fetchDepartmentDetail,
  fetchDepartmentList,
  fetchPostDetail,
  fetchPostList,
  updatePost,
  updateDepartment,
} from '@/api/organization'
import {
  parseDepartmentDetail,
  parseDepartmentOptions,
  parseDepartmentTree,
  parsePostDetail,
  parsePostOptions,
  parsePostPage,
} from '@/api/organization/parsers'
import type { PostCreatePayload } from '@/types'

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

const post = {
  post_id: 4,
  post_code: 'product_manager',
  post_name: '产品经理',
  post_sort: 3,
  status: '1',
  remark: '负责产品规划',
  create_time: '2026-08-10T09:00:00+08:00',
  update_time: '2026-08-10T10:00:00+08:00',
}

describe('岗位 API', () => {
  beforeEach(() => {
    requestJson.mockReset()
    requestJson.mockResolvedValue(null)
  })

  it('按后端分页契约查询岗位列表和详情', async () => {
    await fetchPostList({ page: 2, size: 20 }, { name: ' 产品 ', status: '1' })
    await fetchPostDetail(4)

    expect(requestJson).toHaveBeenNthCalledWith(
      1,
      '/post/list',
      { params: { page: 2, size: 20, name: '产品', status: '1' } },
      expect.any(Function),
    )
    expect(requestJson).toHaveBeenNthCalledWith(2, '/post/4', {}, expect.any(Function))
  })

  it('使用真实方法和路径新增、修改及删除岗位', async () => {
    const payload: PostCreatePayload = {
      post_code: 'product_manager',
      post_name: '产品经理',
      post_sort: 3,
      remark: null,
      status: '1',
    }

    await createPost(payload)
    await updatePost(4, payload)
    await deletePost(4)

    expect(requestJson).toHaveBeenNthCalledWith(
      1,
      '/post/add',
      { method: 'POST', data: payload },
      expect.any(Function),
    )
    expect(requestJson).toHaveBeenNthCalledWith(
      2,
      '/post/4',
      { method: 'PUT', data: payload },
      expect.any(Function),
    )
    expect(requestJson).toHaveBeenNthCalledWith(
      3,
      '/post/4',
      { method: 'DELETE' },
      expect.any(Function),
    )
  })

  it('严格解析岗位分页、详情和精简选项', () => {
    expect(parsePostPage({ items: [post], total: 1, page: 1, size: 20, pages: 1 })).toEqual({
      items: [post],
      total: 1,
      page: 1,
      size: 20,
      pages: 1,
    })
    expect(parsePostDetail(post)).toEqual(post)
    expect(parsePostOptions([post])).toEqual([
      {
        post_id: 4,
        post_code: 'product_manager',
        post_name: '产品经理',
        status: '1',
      },
    ])
  })

  it('拒绝缺少完整字段或分页字段非法的岗位响应', () => {
    expect(() =>
      parsePostPage({
        items: [{ ...post, post_sort: undefined }],
        total: 1,
        page: 1,
        size: 20,
        pages: 1,
      }),
    ).toThrow('接口字段 post_sort 无效')
    expect(() => parsePostPage({ items: [post], total: 1, page: 0, size: 20, pages: 1 })).toThrow(
      '接口字段 page 无效',
    )
  })
})
