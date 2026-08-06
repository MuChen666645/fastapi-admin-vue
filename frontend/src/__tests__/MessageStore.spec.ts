import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

const fetchLatestMessages = vi.hoisted(() => vi.fn())
const fetchUnreadMessageCount = vi.hoisted(() => vi.fn())
const markMessageRead = vi.hoisted(() => vi.fn())
const markAllMessagesRead = vi.hoisted(() => vi.fn())

vi.mock('../api/message', () => ({
  fetchLatestMessages,
  fetchUnreadMessageCount,
  markAllMessagesRead,
  markMessageRead,
}))

import { useMessageStore } from '@/stores'

const message = {
  id: 7,
  message_title: '系统维护通知',
  message_type: 'system' as const,
  message_content: '本周日凌晨进行系统维护',
  publish_time: '2026-08-05T10:00:00+08:00',
  read_at: null,
}

describe('消息 Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    fetchLatestMessages.mockReset()
    fetchUnreadMessageCount.mockReset()
    markMessageRead.mockReset()
    markAllMessagesRead.mockReset()
    fetchLatestMessages.mockResolvedValue({
      system: [message],
      approval: [{ ...message, id: 8, message_type: 'approval' }],
      alarm: [{ ...message, id: 9, message_type: 'alarm', read_at: '2026-08-05T11:00:00+08:00' }],
    })
    fetchUnreadMessageCount.mockResolvedValue({ unread_count: 2 })
    markMessageRead.mockResolvedValue(null)
    markAllMessagesRead.mockResolvedValue({ updated_count: 2 })
  })

  it('加载最新消息和后端未读总数', async () => {
    const store = useMessageStore()

    await expect(store.loadLatest()).resolves.toBe(true)

    expect(fetchLatestMessages).toHaveBeenCalledOnce()
    expect(fetchUnreadMessageCount).toHaveBeenCalledOnce()
    expect(store.latestItems).toHaveLength(3)
    expect(store.latestLoaded).toBe(true)
    expect(store.unreadCount).toBe(2)
  })

  it('标记已读后同步消息和未读数', async () => {
    const store = useMessageStore()
    await store.loadLatest()

    await expect(store.markRead(store.latestItems[0]!)).resolves.toBe(true)

    expect(markMessageRead).toHaveBeenCalledWith(7)
    expect(store.latestItems[0]?.read_at).toEqual(expect.any(String))
    expect(store.unreadCount).toBe(1)
  })

  it('支持全部已读并清零未读数', async () => {
    const store = useMessageStore()
    await store.loadLatest()

    await expect(store.markAllRead()).resolves.toBe(true)

    expect(markAllMessagesRead).toHaveBeenCalledOnce()
    expect(store.unreadCount).toBe(0)
    expect(store.latestItems.every((item) => item.read_at)).toBe(true)
  })

  it('最新消息请求失败时保留错误状态并结束加载', async () => {
    const requestError = new Error('network failed')
    fetchLatestMessages.mockRejectedValueOnce(requestError)
    const store = useMessageStore()

    await expect(store.loadLatest()).resolves.toBe(false)

    expect(store.latestError).toBe(requestError)
    expect(store.latestLoading).toBe(false)
  })
})
