import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { flushPromises, mount } from '@vue/test-utils'
import { defineComponent, ref } from 'vue'

import type { MessageItem } from '@/types'

const mocks = vi.hoisted(() => ({
  notificationInfo: vi.fn(),
  useMessageCenter: vi.fn(),
  useNotification: vi.fn(),
}))

mocks.useNotification.mockReturnValue({ info: mocks.notificationInfo })

vi.mock('naive-ui', () => ({ useNotification: mocks.useNotification }))
vi.mock('../hooks/useLocale', () => ({
  useLocale: () => ({ t: (key: string) => key }),
}))
vi.mock('../hooks/useMessageCenter', () => ({ useMessageCenter: mocks.useMessageCenter }))

import { useMessagePopover } from '@/hooks/useMessagePopover'

const createMessage = (id: number): MessageItem => ({
  id,
  message_title: `消息 ${id}`,
  message_type: 'system',
  message_content: '消息内容',
  publish_time: '2026-08-06 09:30:00',
  read_at: null,
})

describe('useMessagePopover', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    mocks.notificationInfo.mockReset()
    mocks.useMessageCenter.mockReset()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('轮询发现新增未读站内信时显示 Notification', async () => {
    const items = ref<MessageItem[]>([])
    const loaded = ref(false)
    let loadCount = 0
    const openCenter = vi.fn()
    const load = vi.fn(async () => {
      loadCount += 1
      items.value = loadCount === 1 ? [createMessage(1)] : [createMessage(1), createMessage(2)]
      loaded.value = true
      return true
    })
    mocks.useMessageCenter.mockReturnValue({ items, loaded, load, openCenter })

    const wrapper = mount(
      defineComponent({
        setup() {
          useMessagePopover()
          return () => null
        },
      }),
    )

    await flushPromises()
    expect(mocks.notificationInfo).not.toHaveBeenCalled()

    await vi.advanceTimersByTimeAsync(30_000)
    await flushPromises()

    expect(mocks.notificationInfo).toHaveBeenCalledWith(
      expect.objectContaining({
        title: 'message.notification.newTitle',
        content: '消息 2',
        duration: 6000,
      }),
    )

    wrapper.unmount()
  })
})
