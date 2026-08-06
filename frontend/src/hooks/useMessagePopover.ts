import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useNotification } from 'naive-ui'

import type { MessageItem } from '@/types'
import { findNewUnreadMessages } from '@/utils'

import { useLocale } from './useLocale'
import { useMessageCenter } from './useMessageCenter'

const MESSAGE_POLL_INTERVAL_MS = 30_000

export const useMessagePopover = () => {
  const center = useMessageCenter()
  const notification = useNotification()
  const { t } = useLocale()
  const visible = ref(false)
  const previewLoaded = ref(false)
  let pollingTimer: number | null = null
  let loading = false

  const loadLatest = async (notifyNewMessages: boolean): Promise<boolean> => {
    if (loading) {
      return false
    }

    const wasLoaded = center.loaded.value
    const previousItems = [...center.items.value]
    loading = true
    try {
      const loaded = await center.load()
      previewLoaded.value = loaded || previewLoaded.value
      if (loaded && notifyNewMessages && wasLoaded) {
        findNewUnreadMessages(previousItems, center.items.value).forEach((item) => {
          notification.info({
            title: t('message.notification.newTitle'),
            content: item.message_title,
            duration: 6000,
          })
        })
      }
      return loaded
    } finally {
      loading = false
    }
  }

  const open = async (): Promise<void> => {
    visible.value = true
    if (previewLoaded.value || center.loaded.value) {
      previewLoaded.value = true
      return
    }

    await loadLatest(false)
  }

  const close = (): void => {
    visible.value = false
  }

  const toggle = (): void => {
    if (visible.value) {
      close()
      return
    }

    void open()
  }

  const refresh = async (): Promise<void> => {
    await loadLatest(false)
  }

  const selectItem = async (item: MessageItem): Promise<void> => {
    await center.markRead(item)
    close()
    await center.openCenter(item.id)
  }

  const viewAll = async (): Promise<void> => {
    close()
    await center.openCenter()
  }

  onMounted(() => {
    if (!center.loaded.value) {
      void loadLatest(false)
    }
    pollingTimer = window.setInterval(() => {
      void loadLatest(true)
    }, MESSAGE_POLL_INTERVAL_MS)
  })

  onBeforeUnmount(() => {
    if (pollingTimer !== null) {
      window.clearInterval(pollingTimer)
      pollingTimer = null
    }
  })

  return {
    ...center,
    close,
    open,
    refresh,
    selectItem,
    toggle,
    viewAll,
    visible,
  }
}
