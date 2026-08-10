import { beforeEach, describe, expect, it, vi } from 'vitest'

const requestJson = vi.hoisted(() => vi.fn())

vi.mock('../utils/request', () => ({ requestJson }))

import { createMenu, deleteMenu, fetchMenuDetail, fetchMenuList, updateMenu } from '@/api/menu'
import { parseMenuDetail, parseMenuList } from '@/api/menu/parsers'

const menu = {
  menu_id: 4,
  menu_name: '用户管理',
  menu_path: '/system/user',
  parent_id: 1,
  perms: 'system:user:list',
  sort: 1,
  menu_type: 'C',
  link_url: null,
  icon: 'PeopleOutline',
  component: 'system/user/index',
  is_cache: '0',
  is_hidden: '0',
  create_time: '2026-08-10T09:00:00+08:00',
  status: '1',
  update_time: '2026-08-10T10:00:00+08:00',
  remark: null,
  children: [],
}

describe('菜单 API', () => {
  beforeEach(() => {
    requestJson.mockReset()
    requestJson.mockResolvedValue(null)
  })

  it('按后端契约查询菜单树和菜单详情', async () => {
    await fetchMenuList({ menu_name: ' 用户 ', status: '0' })
    await fetchMenuDetail(4)

    expect(requestJson).toHaveBeenNthCalledWith(
      1,
      '/menu/list',
      { params: { menu_name: '用户', status: '0' } },
      expect.any(Function),
    )
    expect(requestJson).toHaveBeenNthCalledWith(2, '/menu/4', {}, expect.any(Function))
  })

  it('按菜单类型发送新增请求体并支持修改删除', async () => {
    await createMenu({
      menu_name: '路由菜单',
      parent_id: 0,
      menu_type: 'C',
      menu_path: '/demo',
      sort: 1,
      icon: 'GridOutline',
      component: 'demo/index',
      is_cache: '0',
      is_hidden: '0',
      remark: null,
    })
    await createMenu({
      menu_name: '按钮权限',
      parent_id: 4,
      menu_type: 'F',
      perms: 'system:user:add',
      sort: 1,
      remark: '新增按钮',
    })
    await createMenu({
      menu_name: '外链菜单',
      parent_id: 1,
      menu_type: 'L',
      menu_path: 'https://example.com',
      sort: null,
      icon: null,
      remark: null,
    })
    await createMenu({
      menu_name: 'Iframe 菜单',
      parent_id: 1,
      menu_type: 'I',
      menu_path: '/iframe',
      component: 'iframe/index',
      link_url: 'https://example.com',
      sort: 2,
      icon: null,
      is_cache: '1',
      is_hidden: '0',
      remark: null,
    })
    await updateMenu(4, { menu_name: '更新后的菜单', status: '0' })
    await deleteMenu(4)

    expect(requestJson).toHaveBeenNthCalledWith(
      1,
      '/menu/add',
      expect.objectContaining({
        method: 'POST',
        data: expect.objectContaining({ menu_type: 'C' }),
      }),
      expect.any(Function),
    )
    expect(requestJson).toHaveBeenNthCalledWith(
      2,
      '/menu/add',
      expect.objectContaining({
        method: 'POST',
        data: expect.objectContaining({ menu_type: 'F' }),
      }),
      expect.any(Function),
    )
    expect(requestJson).toHaveBeenNthCalledWith(
      3,
      '/menu/add',
      expect.objectContaining({
        method: 'POST',
        data: expect.objectContaining({ menu_type: 'L' }),
      }),
      expect.any(Function),
    )
    expect(requestJson).toHaveBeenNthCalledWith(
      4,
      '/menu/add',
      expect.objectContaining({
        method: 'POST',
        data: expect.objectContaining({ menu_type: 'I' }),
      }),
      expect.any(Function),
    )
    expect(requestJson).toHaveBeenNthCalledWith(
      5,
      '/menu/4',
      { method: 'PUT', data: { menu_name: '更新后的菜单', status: '0' } },
      expect.any(Function),
    )
    expect(requestJson).toHaveBeenNthCalledWith(
      6,
      '/menu/4',
      { method: 'DELETE' },
      expect.any(Function),
    )
  })

  it('解析菜单树和详情字段', () => {
    expect(parseMenuList([menu])).toMatchObject([{ menu_id: 4, children: [] }])
    expect(parseMenuDetail({ ...menu, children: undefined })).toMatchObject({
      menu_id: 4,
      menu_name: '用户管理',
    })
  })
})
