import { computed, ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'

import { useLocale } from '@/hooks/useLocale'
import { useMessageStore } from '@/stores'
import { formatMessageRelativeTime, resolveMessageTab } from '@/utils'
import type { MessageItem, MessageTab } from '@/types'

export const useMessageCenter = () => {
  const router = useRouter()
  const store = useMessageStore()
  const { language } = useLocale()
  const { hasUnread, latestError, latestItems, latestLoaded, latestLoading, unreadCount } =
    storeToRefs(store)
  const activeTab = ref<MessageTab>('system')
  const sourceItems = computed(() => latestItems.value)

  const visibleItems = computed(() =>
    sourceItems.value.filter((item) => resolveMessageTab(item.message_type) === activeTab.value),
  )
  const tabUnreadCounts = computed<Record<MessageTab, number>>(() => ({
    system: sourceItems.value.filter(
      (item) => !item.read_at && resolveMessageTab(item.message_type) === 'system',
    ).length,
    approval: sourceItems.value.filter(
      (item) => !item.read_at && resolveMessageTab(item.message_type) === 'approval',
    ).length,
    alarm: sourceItems.value.filter(
      (item) => !item.read_at && resolveMessageTab(item.message_type) === 'alarm',
    ).length,
  }))

  const load = (): Promise<boolean> => store.loadLatest()

  const selectTab = (tab: MessageTab): void => {
    activeTab.value = tab
  }

  const formatTime = (value: string | null): string =>
    formatMessageRelativeTime(value, language.value)

  const openCenter = async (messageId?: number): Promise<void> => {
    await router.push({
      path: '/system/message',
      query: messageId ? { messageId: String(messageId) } : undefined,
    })
  }

  const markRead = (item: MessageItem): Promise<boolean> => store.markRead(item)

  return {
    activeTab,
    error: latestError,
    formatTime,
    hasUnread,
    items: sourceItems,
    loaded: latestLoaded,
    load,
    loading: latestLoading,
    markRead,
    openCenter,
    selectTab,
    tabUnreadCounts,
    unreadCount,
    visibleItems,
  }
}
