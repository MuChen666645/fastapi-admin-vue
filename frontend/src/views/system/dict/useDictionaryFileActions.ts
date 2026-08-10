import { ref } from 'vue'
import { useMessage } from 'naive-ui'

import { exportDictionary, importDictionary } from '@/api'
import { useLocale } from '@/hooks'
import type { DictionaryImportResult } from '@/types'
import { downloadBlob } from '@/utils'

interface DictionaryFileActionsOptions {
  refresh: () => Promise<unknown>
}

export const useDictionaryFileActions = (options: DictionaryFileActionsOptions) => {
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
      const file = await exportDictionary()
      downloadBlob(file.blob, file.filename ?? 'dictionary.xlsx')
      message.success(t('dict.exportSuccess'))
    } finally {
      exportLoading.value = false
    }
  }

  const showImportResult = (result: DictionaryImportResult): void => {
    if (result.failed > 0) {
      message.warning(
        t('dict.importPartial')
          .replace('{imported}', String(result.imported))
          .replace('{failed}', String(result.failed)),
      )
      return
    }

    message.success(t('dict.importSuccess').replace('{count}', String(result.imported)))
  }

  const handleImport = async (file: File): Promise<void> => {
    if (importLoading.value || exportLoading.value) {
      return
    }

    if (!file.name.toLowerCase().endsWith('.xlsx')) {
      message.error(t('dict.importFileType'))
      return
    }

    importLoading.value = true
    try {
      showImportResult(await importDictionary(file))
      await options.refresh()
    } finally {
      importLoading.value = false
    }
  }

  return { exportLoading, handleExport, handleImport, importLoading }
}
