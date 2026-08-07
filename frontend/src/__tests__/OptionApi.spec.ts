import { beforeEach, describe, expect, it, vi } from 'vitest'

const requestJson = vi.hoisted(() => vi.fn())

vi.mock('../utils/request', () => ({ requestJson }))

import { fetchPostOptions } from '@/api/organization'
import { parsePostOptions } from '@/api/organization/parsers'
import { fetchRoleOptions } from '@/api/role'
import { parseRoleOptions } from '@/api/role/parsers'
import { fetchUserOptions } from '@/api/user'
import { parseUserOptions } from '@/api/user/parsers'

describe('下拉选项 API', () => {
  beforeEach(() => {
    requestJson.mockReset()
    requestJson.mockResolvedValue([])
  })

  it('使用独立的角色、用户和岗位下拉接口', async () => {
    await fetchRoleOptions()
    await fetchUserOptions()
    await fetchPostOptions()

    expect(requestJson).toHaveBeenNthCalledWith(1, '/role/options', {}, expect.any(Function))
    expect(requestJson).toHaveBeenNthCalledWith(2, '/user/options', {}, expect.any(Function))
    expect(requestJson).toHaveBeenNthCalledWith(3, '/post/options', {}, expect.any(Function))
  })

  it('严格解析下拉接口响应字段', () => {
    expect(
      parseRoleOptions([
        { id: 1, name: '超级管理员', code: 'admin', status: '1' },
        { id: 2, name: '运营', code: 'operator', status: '1' },
      ]),
    ).toEqual([{ id: 2, name: '运营', code: 'operator', description: null, status: '1' }])
    expect(parseUserOptions([{ id: 7, username: 'alice', nickname: null }])).toEqual([
      { id: 7, username: 'alice', nickname: null },
    ])
    expect(
      parsePostOptions([{ post_id: 4, post_code: 'support', post_name: '客服', status: '1' }]),
    ).toEqual([{ post_id: 4, post_code: 'support', post_name: '客服', status: '1' }])
  })

  it('拒绝角色下拉数据中的超级管理员角色', () => {
    expect(parseRoleOptions([{ id: 1, name: '超级管理员', code: 'ADMIN', status: '1' }])).toEqual(
      [],
    )
  })
})
