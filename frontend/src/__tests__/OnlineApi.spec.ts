import { beforeEach, describe, expect, it, vi } from 'vitest'

const requestJson = vi.hoisted(() => vi.fn())

vi.mock('../utils/request', () => ({ requestJson }))

import { fetchOnlineSessions, forceLogoutSession, forceLogoutUser } from '@/api/online'
import { parseForceLogoutUserResult, parseOnlineSessionPage } from '@/api/online/parsers'

const tokenId = 'a'.repeat(64)
const onlineSession = {
  token_id: tokenId,
  user_id: 7,
  username: 'admin',
  ip_address: '127.0.0.1',
  user_agent: 'Mozilla/5.0',
  login_time: '2026-08-12T09:00:00+08:00',
  expire_time: '2026-08-12T10:00:00+08:00',
}

describe('在线用户 API', () => {
  beforeEach(() => {
    requestJson.mockReset()
    requestJson.mockResolvedValue(null)
  })

  it('按后端契约传递分页、用户名和登录 IP 筛选参数', async () => {
    await fetchOnlineSessions(
      { page: 2, size: 50 },
      { username: ' admin ', ip_address: ' 127.0.0.1 ' },
    )
    await fetchOnlineSessions({ page: 1, size: 20 }, { username: ' ', ip_address: '' })

    expect(requestJson).toHaveBeenNthCalledWith(
      1,
      '/online/list',
      { params: { page: 2, size: 50, username: 'admin', ip_address: '127.0.0.1' } },
      parseOnlineSessionPage,
    )
    expect(requestJson).toHaveBeenNthCalledWith(
      2,
      '/online/list',
      { params: { page: 1, size: 20 } },
      parseOnlineSessionPage,
    )
  })

  it('使用真实删除路径分别下线会话和用户全部会话', async () => {
    await forceLogoutSession(tokenId)
    await forceLogoutUser(7)

    expect(requestJson).toHaveBeenNthCalledWith(
      1,
      `/online/token/${tokenId}`,
      { method: 'DELETE' },
      expect.any(Function),
    )
    expect(requestJson).toHaveBeenNthCalledWith(
      2,
      '/online/user/7',
      { method: 'DELETE' },
      parseForceLogoutUserResult,
    )
  })

  it('严格解析在线会话分页和用户下线结果', () => {
    expect(
      parseOnlineSessionPage({
        items: [onlineSession],
        total: 1,
        page: 1,
        size: 20,
        pages: 1,
      }),
    ).toEqual({ items: [onlineSession], total: 1, page: 1, size: 20, pages: 1 })
    expect(parseForceLogoutUserResult({ user_id: 7, revoked_token_count: 2 })).toEqual({
      user_id: 7,
      revoked_token_count: 2,
    })
  })

  it('拒绝暴露原始令牌形态、非法分页和非法撤销数量', () => {
    expect(() =>
      parseOnlineSessionPage({
        items: [{ ...onlineSession, token_id: 'raw-jwt-token' }],
        total: 1,
        page: 1,
        size: 20,
        pages: 1,
      }),
    ).toThrow('接口字段 token_id 无效')
    expect(() =>
      parseOnlineSessionPage({
        items: [onlineSession],
        total: 1,
        page: 0,
        size: 20,
        pages: 1,
      }),
    ).toThrow('接口字段 page 无效')
    expect(() => parseForceLogoutUserResult({ user_id: 7, revoked_token_count: -1 })).toThrow(
      '接口字段 revoked_token_count 无效',
    )
  })
})
