import type {
  MessageItem,
  MessageTab,
  MessageType,
  MessageVisualTone,
  PreferenceLanguage,
} from '@/types'

const MINUTE_IN_SECONDS = 60
const HOUR_IN_SECONDS = MINUTE_IN_SECONDS * 60
const DAY_IN_SECONDS = HOUR_IN_SECONDS * 24
const WEEK_IN_SECONDS = DAY_IN_SECONDS * 7
const MONTH_IN_SECONDS = DAY_IN_SECONDS * 30
const YEAR_IN_SECONDS = DAY_IN_SECONDS * 365

export const resolveMessageTab = (messageType: string): MessageTab => {
  const normalizedType = messageType.trim().toLowerCase()
  if (normalizedType === 'approval') {
    return 'approval'
  }

  if (normalizedType === 'alarm') {
    return 'alarm'
  }

  return 'system'
}

export const resolveMessageTone = (messageType: string): MessageVisualTone => {
  const normalizedType = messageType.trim().toLowerCase()
  if (normalizedType === 'alarm') {
    return 'danger'
  }

  if (normalizedType === 'approval') {
    return 'warning'
  }

  return 'info'
}

export const findNewUnreadMessages = (
  previousItems: readonly MessageItem[],
  currentItems: readonly MessageItem[],
): MessageItem[] => {
  const previousIds = new Set(previousItems.map((item) => item.id))
  return currentItems.filter((item) => !item.read_at && !previousIds.has(item.id))
}

const relativeTimeParts = (
  seconds: number,
): { value: number; unit: Intl.RelativeTimeFormatUnit } => {
  const absoluteSeconds = Math.abs(seconds)
  if (absoluteSeconds < MINUTE_IN_SECONDS) {
    return { value: Math.round(seconds), unit: 'second' }
  }

  if (absoluteSeconds < HOUR_IN_SECONDS) {
    return { value: Math.round(seconds / MINUTE_IN_SECONDS), unit: 'minute' }
  }

  if (absoluteSeconds < DAY_IN_SECONDS) {
    return { value: Math.round(seconds / HOUR_IN_SECONDS), unit: 'hour' }
  }

  if (absoluteSeconds < WEEK_IN_SECONDS) {
    return { value: Math.round(seconds / DAY_IN_SECONDS), unit: 'day' }
  }

  if (absoluteSeconds < MONTH_IN_SECONDS) {
    return { value: Math.round(seconds / WEEK_IN_SECONDS), unit: 'week' }
  }

  return {
    value: Math.round(
      seconds / (absoluteSeconds < YEAR_IN_SECONDS ? MONTH_IN_SECONDS : YEAR_IN_SECONDS),
    ),
    unit: absoluteSeconds < YEAR_IN_SECONDS ? 'month' : 'year',
  }
}

export const formatMessageRelativeTime = (
  value: string | null,
  language: PreferenceLanguage,
  now = Date.now(),
): string => {
  if (!value) {
    return ''
  }

  const timestamp = Date.parse(value)
  if (Number.isNaN(timestamp)) {
    return value
  }

  const seconds = (timestamp - now) / 1000
  const absoluteSeconds = Math.abs(seconds)
  if (absoluteSeconds < YEAR_IN_SECONDS) {
    const { value: relativeValue, unit } = relativeTimeParts(seconds)
    return new Intl.RelativeTimeFormat(language, { numeric: 'auto' }).format(relativeValue, unit)
  }

  return new Intl.DateTimeFormat(language, { month: '2-digit', day: '2-digit' }).format(timestamp)
}

export const parseRecipientUserIds = (value: string): number[] => {
  const source = value.trim()
  if (!source) {
    return []
  }

  const ids = source.split(',').map((item) => item.trim())
  if (ids.some((item) => !/^\d+$/.test(item) || Number(item) < 1)) {
    throw new Error('接收人 ID 必须是以逗号分隔的正整数')
  }

  return [...new Set(ids.map(Number))]
}

export const toMessagePublishTime = (value: number | null): string | null =>
  value === null ? null : new Date(value).toISOString()

export const toMessageFormTime = (value: string | null): number | null => {
  if (!value) {
    return null
  }

  const timestamp = Date.parse(value)
  return Number.isNaN(timestamp) ? null : timestamp
}

export const isMessageType = (value: string): value is MessageType =>
  value === 'system' || value === 'approval' || value === 'alarm'
