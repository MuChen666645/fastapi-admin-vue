import type moment from 'moment'

export type MomentInput = moment.MomentInput
export type MomentInputValue = MomentInput | null
export type MomentFormatSpecification = moment.MomentFormatSpecification
export type MomentInstance = moment.Moment
export type MomentUnit = moment.unitOfTime.StartOf

export interface MomentFormatOptions {
  format?: string
  fallback?: string
}

export interface MomentParseOptions {
  format?: MomentFormatSpecification
  strict?: boolean
}

export interface MomentRange {
  start: MomentInstance
  end: MomentInstance
}
