export type UtilsDemoFormat = 'date' | 'datetime' | 'time'

export interface UtilsDemoModel {
  value: string
  format: UtilsDemoFormat
  strict: boolean
}

export interface UtilsDemoResult {
  valid: boolean
  locale: string
  parsed: string
  formatted: string
  iso: string
  range: string
  relative: string
}
