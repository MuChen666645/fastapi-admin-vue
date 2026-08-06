import { ref } from 'vue'

import type { MessageItem } from '@/types'

import { useMessageCenter } from './useMessageCenter'

export const useMessagePopover = () => {
  const center = useMessageCenter()
  const visible = ref(false)
  const previewLoaded = ref(false)

  const open = async (): Promise<void> => {
    visible.value = true
    if (previewLoaded.value) {
      return
    }

    const loaded = await center.load()
    previewLoaded.value = loaded
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
    previewLoaded.value = await center.load()
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
