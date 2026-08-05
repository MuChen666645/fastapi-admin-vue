import moment from 'moment'

import type {
  MomentFormatOptions,
  MomentFormatSpecification,
  MomentInputValue,
  MomentInstance,
  MomentParseOptions,
  MomentRange,
  MomentUnit,
} from '@/types'

export const MOMENT_LOCALE = 'zh-cn'
export const DEFAULT_DATE_FORMAT = 'YYYY-MM-DD'
export const DEFAULT_DATETIME_FORMAT = 'YYYY-MM-DD HH:mm:ss'
export const DEFAULT_TIME_FORMAT = 'HH:mm:ss'

const toMomentInstance = (
  value?: MomentInputValue,
  format?: MomentFormatSpecification,
  strict = false,
): MomentInstance => {
  const instance = format === undefined ? moment(value, strict) : moment(value, format, strict)
  return instance.locale(MOMENT_LOCALE)
}

export const createMoment = (
  value?: MomentInputValue,
  options: MomentParseOptions = {},
): MomentInstance => toMomentInstance(value, options.format, options.strict ?? false)

export const parseMoment = (
  value: MomentInputValue,
  options: MomentParseOptions = {},
): MomentInstance | null => {
  if (value === null || value === undefined) {
    return null
  }

  const instance = createMoment(value, { ...options, strict: options.strict ?? true })
  return instance.isValid() ? instance : null
}

export const isValidMoment = (value: MomentInputValue, options: MomentParseOptions = {}): boolean =>
  parseMoment(value, options) !== null

export const formatMoment = (
  value: MomentInputValue,
  options: MomentFormatOptions = {},
): string => {
  const instance = parseMoment(value)
  return instance?.format(options.format ?? DEFAULT_DATETIME_FORMAT) ?? options.fallback ?? ''
}

export const formatDate = (value: MomentInputValue, options: MomentFormatOptions = {}): string =>
  formatMoment(value, { ...options, format: options.format ?? DEFAULT_DATE_FORMAT })

export const formatDateTime = (
  value: MomentInputValue,
  options: MomentFormatOptions = {},
): string => formatMoment(value, { ...options, format: options.format ?? DEFAULT_DATETIME_FORMAT })

export const formatTime = (value: MomentInputValue, options: MomentFormatOptions = {}): string =>
  formatMoment(value, { ...options, format: options.format ?? DEFAULT_TIME_FORMAT })

export const formatRelativeTime = (
  value: MomentInputValue,
  withoutSuffix = false,
  fallback = '',
): string => parseMoment(value)?.fromNow(withoutSuffix) ?? fallback

export const getDateRange = (
  value: MomentInputValue,
  unit: MomentUnit = 'day',
): MomentRange | null => {
  const instance = parseMoment(value)
  if (!instance) {
    return null
  }

  return {
    start: instance.clone().startOf(unit),
    end: instance.clone().endOf(unit),
  }
}

export const toDate = (value: MomentInputValue): Date | null => parseMoment(value)?.toDate() ?? null

export const toISOString = (value: MomentInputValue, fallback = ''): string =>
  parseMoment(value)?.toISOString() ?? fallback
