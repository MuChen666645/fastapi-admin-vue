import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import {
  fetchLatestMessages,
  fetchUnreadMessageCount,
  markAllMessagesRead,
  markMessageRead,
} from '@/api/message'
import type { MessageItem } from '@/types'

export const useMessageStore = defineStore('message', () => {
  const latestItems = ref<MessageItem[]>([])
  const unreadCount = ref(0)
  const latestLoading = ref(false)
  const latestError = ref<Error | null>(null)
  const latestLoaded = ref(false)
  let latestRequestVersion = 0

  const hasUnread = computed(() => unreadCount.value > 0)

  const loadLatest = async (): Promise<boolean> => {
    const requestId = latestRequestVersion + 1
    latestRequestVersion = requestId
    latestLoading.value = true
    latestError.value = null

    try {
      const [latestResult, unreadResult] = await Promise.all([
        fetchLatestMessages(),
        fetchUnreadMessageCount(),
      ])
      if (requestId !== latestRequestVersion) {
        return false
      }

      latestItems.value = [...latestResult.system, ...latestResult.approval, ...latestResult.alarm]
      unreadCount.value = unreadResult.unread_count
      latestLoaded.value = true
      return true
    } catch (requestError) {
      if (requestId === latestRequestVersion) {
        latestError.value =
          requestError instanceof Error ? requestError : new Error('消息加载失败，请稍后重试')
      }
      return false
    } finally {
      if (requestId === latestRequestVersion) {
        latestLoading.value = false
      }
    }
  }

  const markLocalRead = (messageId: number): void => {
    const item = latestItems.value.find((candidate) => candidate.id === messageId)
    if (!item || item.read_at) {
      return
    }

    item.read_at = new Date().toISOString()
    unreadCount.value = Math.max(0, unreadCount.value - 1)
  }

  const markRead = async (item: MessageItem): Promise<boolean> => {
    if (item.read_at) {
      return true
    }

    try {
      await markMessageRead(item.id)
      markLocalRead(item.id)
      return true
    } catch (requestError) {
      latestError.value =
        requestError instanceof Error ? requestError : new Error('消息已读操作失败，请稍后重试')
      return false
    }
  }

  const markAllRead = async (): Promise<boolean> => {
    try {
      await markAllMessagesRead()
      latestItems.value.forEach((item) => {
        item.read_at ??= new Date().toISOString()
      })
      unreadCount.value = 0
      return true
    } catch (requestError) {
      latestError.value =
        requestError instanceof Error ? requestError : new Error('全部已读操作失败，请稍后重试')
      return false
    }
  }

  const reset = (): void => {
    latestRequestVersion += 1
    latestItems.value = []
    unreadCount.value = 0
    latestLoading.value = false
    latestError.value = null
    latestLoaded.value = false
  }

  return {
    hasUnread,
    latestError,
    latestItems,
    latestLoaded,
    latestLoading,
    loadLatest,
    markAllRead,
    markLocalRead,
    markRead,
    reset,
    unreadCount,
  }
})
