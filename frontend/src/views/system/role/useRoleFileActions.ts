import { ref } from 'vue'
import { useMessage } from 'naive-ui'

import { exportRoles, importRoles } from '@/api'
import { useLocale } from '@/hooks'
import type { RoleImportResult } from '@/types'
import { downloadBlob } from '@/utils'

interface RoleFileActionsOptions {
  refresh: () => Promise<unknown>
}

export const useRoleFileActions = (options: RoleFileActionsOptions) => {
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
      const file = await exportRoles()
      downloadBlob(file.blob, file.filename ?? 'roles.xlsx')
      message.success(t('role.exportSuccess'))
    } finally {
      exportLoading.value = false
    }
  }

  const showImportResult = (result: RoleImportResult): void => {
    if (result.failed > 0) {
      message.warning(
        t('role.importPartial')
          .replace('{imported}', String(result.imported))
          .replace('{failed}', String(result.failed)),
      )
      return
    }

    message.success(t('role.importSuccess').replace('{count}', String(result.imported)))
  }

  const handleImport = async (file: File): Promise<void> => {
    if (importLoading.value || exportLoading.value) {
      return
    }

    if (!file.name.toLowerCase().endsWith('.xlsx')) {
      message.error(t('role.importFileType'))
      return
    }

    importLoading.value = true
    try {
      showImportResult(await importRoles(file))
      await options.refresh()
    } finally {
      importLoading.value = false
    }
  }

  return { exportLoading, handleExport, handleImport, importLoading }
}
