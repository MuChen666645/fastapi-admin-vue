import { ref } from 'vue'
import { useMessage } from 'naive-ui'

import { exportUsers, importUsers } from '@/api'
import { useLocale } from '@/hooks'
import type { UserImportResult } from '@/types'
import { downloadBlob } from '@/utils'

interface UserFileActionsOptions {
  refresh: () => Promise<unknown>
}

export const useUserFileActions = (options: UserFileActionsOptions) => {
  const { t } = useLocale()
  const message = useMessage()
  const exportLoading = ref(false)
  const importLoading = ref(false)

  const handleExport = async (): Promise<void> => {
    if (exportLoading.value || importLoading.value) {
      return
    }

    exportLoading.value = true
    try {
      const file = await exportUsers()
      downloadBlob(file.blob, file.filename ?? 'users.xlsx')
      message.success(t('user.exportSuccess'))
    } finally {
      exportLoading.value = false
    }
  }

  const showImportResult = (result: UserImportResult): void => {
    if (result.failed > 0) {
      message.warning(
        t('user.importPartial')
          .replace('{imported}', String(result.imported))
          .replace('{failed}', String(result.failed)),
      )
      return
    }

    message.success(t('user.importSuccess').replace('{count}', String(result.imported)))
  }

  const handleImport = async (file: File): Promise<void> => {
    if (importLoading.value || exportLoading.value) {
      return
    }

    if (!file.name.toLowerCase().endsWith('.xlsx')) {
      message.error(t('user.importFileType'))
      return
    }

    importLoading.value = true
    try {
      const result = await importUsers(file)
      showImportResult(result)
      await options.refresh()
    } finally {
      importLoading.value = false
    }
  }

  return { exportLoading, handleExport, handleImport, importLoading }
}
