import { describe, expect, it } from 'vitest'

import { parseCurrentUserResponse, parseUserRoutes } from '../api/user/parsers'
import { parseTokenResponse } from '../api/auth/parsers'

describe('API 响应字段解析', () => {
  it('只要求令牌关键字段有效', () => {
    expect(
      parseTokenResponse({
        access_token: 'access-token',
        refresh_token: 'refresh-token',
        token_type: 123,
        expires_in: 'unknown',
        must_change_password: false,
      }),
    ).toEqual({
      access_token: 'access-token',
      refresh_token: 'refresh-token',
      token_type: 'bearer',
      expires_in: null,
      must_change_password: false,
    })

    expect(() =>
      parseTokenResponse({
        access_token: 'access-token',
        refresh_token: 'refresh-token',
        must_change_password: 'invalid',
      }),
    ).toThrow('接口字段 must_change_password 无效')

    expect(() => parseTokenResponse({ refresh_token: 'refresh-token' })).toThrow(
      '接口字段 access_token 无效',
    )
  })

  it('忽略非关键的用户和角色字段异常', () => {
    expect(
      parseCurrentUserResponse({
        user: {
          id: 1,
          username: 'admin',
          nickname: 123,
          email: {},
          phone: false,
          avatar: [],
          status: {},
        },
        roles: [{ id: 'invalid', name: 123, code: null }, 'invalid'],
        permissions: ['system:user:view', 123, null],
      }),
    ).toMatchObject({
      user: {
        nickname: null,
        email: null,
        phone: null,
        avatar: null,
        status: '0',
      },
      roles: [{ id: 0, name: '', code: '' }],
      permissions: ['system:user:view'],
      posts: [],
    })

    expect(() =>
      parseCurrentUserResponse({
        user: { id: 1, username: 'admin' },
        permissions: 'invalid',
      }),
    ).toThrow('当前用户权限响应无效')
  })

  it('对非关键路由元数据使用默认值，但仍拒绝不安全路径', () => {
    expect(
      parseUserRoutes([
        {
          path: 'dashboard',
          name: 'dashboard',
          component: {},
          meta: { title: 123, icon: {}, noCache: 'invalid' },
          children: 'invalid',
        },
      ]),
    ).toMatchObject([
      {
        path: 'dashboard',
        name: 'dashboard',
        component: null,
        redirect: null,
        hidden: false,
        meta: { title: 'dashboard', icon: null, noCache: true, link: null },
        children: [],
      },
    ])

    expect(
      parseUserRoutes([
        {
          path: 'dashboard',
          name: 'dashboard',
          redirect: '../admin',
          meta: {},
          children: [],
        },
      ]),
    ).toEqual([])
  })
})
