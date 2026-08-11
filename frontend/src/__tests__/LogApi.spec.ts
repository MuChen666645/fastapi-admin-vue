import { beforeEach, describe, expect, it, vi } from 'vitest'

const requestJson = vi.hoisted(() => vi.fn())

vi.mock('../utils/request', () => ({ requestJson }))

import { deleteLogs, fetchLogList } from '@/api/log'
import { parseLogPage } from '@/api/log/parsers'

const loginLog = {
  id: 1,
  user_id: 5,
  username: 'admin',
  ip_address: '127.0.0.1',
  user_agent: 'Mozilla/5.0',
  status: '1',
  message: '登录成功',
  login_time: '2026-08-11T09:00:00+08:00',
}

const operationLog = {
  id: 2,
  user_id: 5,
  username: 'admin',
  method: 'GET',
  path: '/api/v1/user/list',
  ip_address: '127.0.0.1',
  user_agent: 'Mozilla/5.0',
  status_code: 200,
  duration_ms: 24,
  operation_time: '2026-08-11T09:10:00+08:00',
}

const exceptionLog = {
  id: 3,
  user_id: null,
  username: null,
  method: 'POST',
  path: '/api/v1/user/login/username',
  ip_address: '127.0.0.1',
  exception_type: 'ValueError',
  exception_message: '参数无效',
  traceback: 'Traceback...',
  exception_time: '2026-08-11T09:20:00+08:00',
}

describe('日志 API', () => {
  beforeEach(() => {
    requestJson.mockReset()
    requestJson.mockResolvedValue(null)
  })

  it('按日志类型传递后端支持的分页和筛选参数', async () => {
    await fetchLogList(
      'login',
      { page: 2, size: 20 },
      { username: ' admin ', status: '1', path: ' /login ', time_range: null },
    )
    await fetchLogList(
      'operation',
      { page: 1, size: 50 },
      { username: '', status: '0', path: ' /api/v1/user/list ', time_range: null },
    )

    expect(requestJson).toHaveBeenNthCalledWith(
      1,
      '/log/login/list',
      { params: { page: 2, size: 20, username: 'admin', status: '1' } },
      expect.any(Function),
    )
    expect(requestJson).toHaveBeenNthCalledWith(
      2,
      '/log/operation/list',
      { params: { page: 1, size: 50, path: '/api/v1/user/list' } },
      expect.any(Function),
    )
  })

  it('按真实路径和请求体批量删除指定类型的日志', async () => {
    await deleteLogs('exception', { ids: [3, 4] })

    expect(requestJson).toHaveBeenCalledWith(
      '/log/exception/batch',
      { method: 'DELETE', data: { ids: [3, 4] } },
      expect.any(Function),
    )
  })

  it('严格解析三类分页日志响应', () => {
    expect(
      parseLogPage({ items: [loginLog], total: 1, page: 1, size: 20, pages: 1 }, 'login'),
    ).toEqual({ items: [loginLog], total: 1, page: 1, size: 20, pages: 1 })
    expect(
      parseLogPage({ items: [operationLog], total: 1, page: 1, size: 20, pages: 1 }, 'operation'),
    ).toEqual({ items: [operationLog], total: 1, page: 1, size: 20, pages: 1 })
    expect(
      parseLogPage({ items: [exceptionLog], total: 1, page: 1, size: 20, pages: 1 }, 'exception'),
    ).toEqual({ items: [exceptionLog], total: 1, page: 1, size: 20, pages: 1 })
  })

  it('拒绝日志必填字段缺失和非法分页字段', () => {
    expect(() =>
      parseLogPage(
        {
          items: [{ ...exceptionLog, exception_type: undefined }],
          total: 1,
          page: 1,
          size: 20,
          pages: 1,
        },
        'exception',
      ),
    ).toThrow('接口字段 exception_type 无效')
    expect(() =>
      parseLogPage({ items: [loginLog], total: 1, page: 0, size: 20, pages: 1 }, 'login'),
    ).toThrow('接口字段 page 无效')
  })
})
