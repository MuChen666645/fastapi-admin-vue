import type { TranslationKey } from '@/types'

export const getJobExecutionStatusTone = (status: string | null) => {
  switch (status) {
    case 'success':
      return 'success' as const
    case 'failed':
      return 'error' as const
    case 'skipped':
      return 'warning' as const
    case 'queued':
      return 'info' as const
    default:
      return 'default' as const
  }
}

export const getJobExecutionStatusLabel = (
  status: string | null,
  t: (key: TranslationKey) => string,
): string => {
  const statusKeys: Record<string, TranslationKey> = {
    success: 'job.execution.success',
    failed: 'job.execution.failed',
    skipped: 'job.execution.skipped',
    queued: 'job.execution.queued',
  }

  return status ? (statusKeys[status] ? t(statusKeys[status]) : status) : t('job.execution.never')
}
