import { describe, expect, it } from 'vitest'

import {
  createMoment,
  formatDate,
  formatDateTime,
  formatRelativeTime,
  formatTime,
  getDateRange,
  isValidMoment,
  parseMoment,
  toDate,
  toISOString,
} from '../utils'

describe('moment utilities', () => {
  it('formats valid values with project defaults and fallback text', () => {
    expect(formatDate('2026-08-05')).toBe('2026-08-05')
    expect(formatDateTime('2026-08-05 13:14:15')).toBe('2026-08-05 13:14:15')
    expect(formatTime('2026-08-05 13:14:15')).toBe('13:14:15')
    expect(formatDate('invalid-date', { fallback: '未设置' })).toBe('未设置')
  })

  it('supports strict format parsing', () => {
    expect(parseMoment('2024-02-29', { format: 'YYYY-MM-DD' })).not.toBeNull()
    expect(parseMoment('2025-02-29', { format: 'YYYY-MM-DD' })).toBeNull()
    expect(isValidMoment('2026/08/05', { format: 'YYYY-MM-DD' })).toBe(false)
  })

  it('uses the configured locale without exposing global setup', () => {
    const instance = createMoment('2026-08-05', { format: 'YYYY-MM-DD', strict: true })

    expect(instance.locale()).toBe('zh-cn')
    expect(instance.format('dddd')).toBe('星期三')
    expect(formatRelativeTime('invalid-date', true, '未设置')).toBe('未设置')
  })

  it('returns independent start and end moments for a date range', () => {
    const range = getDateRange('2026-08-05 13:14:15')

    expect(range?.start.format('YYYY-MM-DD HH:mm:ss')).toBe('2026-08-05 00:00:00')
    expect(range?.end.format('YYYY-MM-DD HH:mm:ss')).toBe('2026-08-05 23:59:59')
    expect(range?.start.valueOf()).toBeLessThan(range?.end.valueOf() ?? 0)
  })

  it('converts valid values and safely handles invalid values', () => {
    expect(toDate('invalid-date')).toBeNull()
    expect(toISOString('invalid-date', '未设置')).toBe('未设置')
    expect(toISOString('2026-08-05T00:00:00.000Z')).toBe('2026-08-05T00:00:00.000Z')
  })
})
