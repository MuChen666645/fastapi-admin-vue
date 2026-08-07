import { ref, type Ref } from 'vue'
import { useDialog, useMessage } from 'naive-ui'

import { batchDeleteUsers, batchUpdateUserStatus } from '@/api'
import { useLocale } from '@/hooks'
import type { UserStatus } from '@/types'

interface UserBatchActionsOptions {
  refresh: () => Promise<unknown>
  selectedUserIds: Ref<number[]>
}

export const useUserBatchActions = (options: UserBatchActionsOptions) => {
  const { t } = useLocale()
  const dialog = useDialog()
  const message = useMessage()
  const batchLoading = ref(false)

  const clearSelection = (): void => {
    options.selectedUserIds.value = []
  }

  const handleSelectionChange = (userIds: number[]): void => {
    options.selectedUserIds.value = userIds
  }

  const handleBatchStatus = async (status: UserStatus): Promise<void> => {
    if (batchLoading.value || options.selectedUserIds.value.length === 0) {
      return
    }

    const userIds = [...options.selectedUserIds.value]
    batchLoading.value = true
    try {
      await batchUpdateUserStatus({ user_ids: userIds, status })
      message.success(
        t(status === '1' ? 'user.batchEnableSuccess' : 'user.batchDisableSuccess').replace(
          '{count}',
          String(userIds.length),
        ),
      )
      clearSelection()
      await options.refresh()
    } finally {
      batchLoading.value = false
    }
  }

  const confirmBatchDelete = (): void => {
    if (batchLoading.value || options.selectedUserIds.value.length === 0) {
      return
    }

    const userIds = [...options.selectedUserIds.value]
    dialog.warning({
      title: t('user.action.confirmBatchDelete'),
      content: t('user.action.confirmBatchDeleteContent').replace(
        '{count}',
        String(userIds.length),
      ),
      positiveText: t('user.action.batchDelete'),
      negativeText: t('user.form.cancel'),
      onPositiveClick: async () => {
        batchLoading.value = true
        try {
          await batchDeleteUsers({ user_ids: userIds })
          message.success(t('user.batchDeleteSuccess').replace('{count}', String(userIds.length)))
          clearSelection()
          await options.refresh()
        } finally {
          batchLoading.value = false
        }
      },
    })
  }

  return {
    batchLoading,
    clearSelection,
    confirmBatchDelete,
    handleBatchStatus,
    handleSelectionChange,
  }
}
