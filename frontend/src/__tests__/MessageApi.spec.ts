import { describe, expect, it, vi } from 'vitest'

const requestJson = vi.hoisted(() => vi.fn())

vi.mock('../utils/request', () => ({ requestJson }))

import {
  createMessage,
  fetchLatestMessages,
  fetchMessageList,
  markAllMessagesRead,
  markMessageRead,
} from '@/api/message'
import { parseMessageLatest, parseMessageListPage } from '@/api/message/parsers'

const listResponse = {
  items: [
    {
      id: 7,
      message_title: 'System maintenance',
      message_type: 'system',
      message_content: 'Maintenance details',
      status: '1',
      publish_time: '2026-08-05T10:00:00+08:00',
      create_by: 1,
      create_time: '2026-08-05T09:00:00+08:00',
      update_time: '2026-08-05T09:00:00+08:00',
    },
  ],
  total: 1,
  page: 1,
  size: 20,
  pages: 1,
}

const filters = {
  title: 'maintenance',
  content: 'details',
  message_type: 'system' as const,
  status: '1' as const,
  publish_time: null,
}

describe('消息 API', () => {
  it('按后端契约构造管理消息列表查询参数', async () => {
    requestJson.mockResolvedValueOnce(listResponse)

    await fetchMessageList({ page: 2, size: 50 }, filters)

    expect(requestJson).toHaveBeenCalledWith(
      '/message/list?page=2&size=50&title=maintenance&content=details&message_type=system&status=1',
      {},
      expect.any(Function),
    )
  })

  it('查询最新消息和后端字段', async () => {
    requestJson.mockResolvedValueOnce({ system: [], approval: [], alarm: [] })

    await fetchLatestMessages()

    expect(requestJson).toHaveBeenCalledWith(
      '/message/latest',
      { showMessage: false },
      expect.any(Function),
    )
    expect(parseMessageLatest({ system: [], approval: [], alarm: [] })).toEqual({
      system: [],
      approval: [],
      alarm: [],
    })
  })

  it('使用 POST 标记消息已读和全部已读', async () => {
    requestJson.mockResolvedValueOnce(null).mockResolvedValueOnce({ updated_count: 2 })

    await markMessageRead(7)
    await markAllMessagesRead()

    expect(requestJson).toHaveBeenNthCalledWith(
      1,
      '/message/7/read',
      { method: 'POST', showMessage: false },
      expect.any(Function),
    )
    expect(requestJson).toHaveBeenNthCalledWith(
      2,
      '/message/read-all',
      { method: 'POST', showMessage: false },
      expect.any(Function),
    )
  })

  it('使用真实 message_* 字段创建消息', async () => {
    requestJson.mockResolvedValueOnce(listResponse.items[0])

    await createMessage({
      message_title: 'New message',
      message_type: 'system',
      message_content: 'Content',
      status: '1',
      publish_time: null,
      recipient_user_ids: [],
      delivery_channels: ['inbox'],
    })

    expect(requestJson).toHaveBeenCalledWith(
      '/message/add',
      {
        method: 'POST',
        data: {
          message_title: 'New message',
          message_type: 'system',
          message_content: 'Content',
          status: '1',
          publish_time: null,
          recipient_user_ids: [],
          delivery_channels: ['inbox'],
        },
      },
      expect.any(Function),
    )
  })

  it('拒绝缺少消息字段的列表响应', () => {
    expect(() => parseMessageListPage({ ...listResponse, items: [{ id: 7 }] })).toThrow(
      '接口字段 message_title 无效',
    )
  })
})
