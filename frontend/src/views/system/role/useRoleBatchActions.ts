import { ref, type Ref } from 'vue'
import { useDialog, useMessage } from 'naive-ui'

import { batchUpdateRoleStatus } from '@/api'
import { useLocale } from '@/hooks'
import type { RoleStatus } from '@/types'

interface RoleBatchActionsOptions {
  refresh: () => Promise<unknown>
  selectedRoleIds: Ref<number[]>
}

export const useRoleBatchActions = (options: RoleBatchActionsOptions) => {
  const { t } = useLocale()
  const dialog = useDialog()
  const message = useMessage()
  const batchLoading = ref(false)

  const clearSelection = (): void => {
    options.selectedRoleIds.value = []
  }

  const handleSelectionChange = (roleIds: number[]): void => {
    options.selectedRoleIds.value = roleIds
  }

  const updateStatus = async (status: RoleStatus): Promise<void> => {
    if (batchLoading.value || options.selectedRoleIds.value.length === 0) {
      return
    }

    const roleIds = [...options.selectedRoleIds.value]
    batchLoading.value = true
    try {
      await batchUpdateRoleStatus({ role_ids: roleIds, status })
      message.success(
        t(status === '1' ? 'role.batchEnableSuccess' : 'role.batchDisableSuccess').replace(
          '{count}',
          String(roleIds.length),
        ),
      )
      clearSelection()
      await options.refresh()
    } finally {
      batchLoading.value = false
    }
  }

  const confirmStatus = (status: RoleStatus): void => {
    if (batchLoading.value || options.selectedRoleIds.value.length === 0) {
      return
    }

    const roleIds = [...options.selectedRoleIds.value]
    dialog.warning({
      title: t('role.action.confirmBatchStatus'),
      content: t('role.action.confirmBatchStatusContent').replace(
        '{count}',
        String(roleIds.length),
      ),
      positiveText: status === '1' ? t('role.action.batchEnable') : t('role.action.batchDisable'),
      negativeText: t('role.form.cancel'),
      onPositiveClick: () => updateStatus(status),
    })
  }

  return { batchLoading, clearSelection, confirmStatus, handleSelectionChange }
}
