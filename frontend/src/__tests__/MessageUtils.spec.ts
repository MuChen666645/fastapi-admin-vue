import { describe, expect, it } from 'vitest'

import { findNewUnreadMessages } from '@/utils'
import type { MessageItem } from '@/types'

const createMessage = (id: number, readAt: string | null = null): MessageItem => ({
  id,
  message_title: `消息 ${id}`,
  message_type: 'system',
  message_content: '消息内容',
  publish_time: '2026-08-06 09:30:00',
  read_at: readAt,
})

describe('消息工具', () => {
  it('只识别新增的未读站内信', () => {
    const previousItems = [createMessage(1)]
    const currentItems = [
      createMessage(1),
      createMessage(2),
      createMessage(3, '2026-08-06 10:00:00'),
    ]

    expect(findNewUnreadMessages(previousItems, currentItems).map((item) => item.id)).toEqual([2])
  })
})
