import type { Component } from 'vue'
import type { FormInst, FormItemRule, FormRules, FormValidationError } from 'naive-ui'

export type AppFormRecord = Record<string, unknown>
export type AppFormPathSegment = string | number
export type AppFormPath = AppFormPathSegment | readonly AppFormPathSegment[]
export type AppFormSize = 'small' | 'medium' | 'large'
export type AppFormLabelPlacement = 'left' | 'top'
export type AppFormLabelAlign = 'left' | 'center' | 'right'
export type AppFormResponsive = 'self' | 'screen'
export type AppFormFieldType =
  | 'input'
  | 'password'
  | 'textarea'
  | 'number'
  | 'select'
  | 'cascader'
  | 'switch'
  | 'date'
  | 'custom'

export interface AppFormFieldContext<T extends object = AppFormRecord> {
  model: T
  field: AppFormField<T>
  group?: AppFormGroup<T>
  index?: number
  path: string
  value: unknown
}

export type AppFormFieldResolver<T extends object = AppFormRecord> =
  boolean | ((context: AppFormFieldContext<T>) => boolean)

export type AppFormFieldPropsResolver<T extends object = AppFormRecord> =
  Record<string, unknown> | ((context: AppFormFieldContext<T>) => Record<string, unknown>)

export interface AppFormField<T extends object = AppFormRecord> {
  key: string
  path: AppFormPath
  label?: string
  type?: AppFormFieldType
  component?: Component
  componentProps?: AppFormFieldPropsResolver<T>
  valueProp?: string
  valueEvent?: string
  rules?: FormItemRule | FormItemRule[]
  required?: boolean
  requiredMessage?: string
  disabled?: AppFormFieldResolver<T>
  hidden?: AppFormFieldResolver<T>
  span?: number | string | ((context: AppFormFieldContext<T>) => number | string)
  showFeedback?: boolean
  feedback?: string
}

export interface AppFormGroup<T extends object = AppFormRecord> {
  key: string
  path: AppFormPath
  title?: string
  description?: string
  fields: ReadonlyArray<AppFormField<T>>
  itemKey?: string
  addable?: boolean
  removable?: boolean
  minItems?: number
  maxItems?: number
  defaultValue?: AppFormRecord
  createItem?: () => AppFormRecord
  addText?: string
  removeText?: string
  emptyText?: string
}

export interface AppFormLayout {
  labelPlacement?: AppFormLabelPlacement
  labelWidth?: number | string
  labelAlign?: AppFormLabelAlign
  size?: AppFormSize
  inline?: boolean
  showFeedback?: boolean
  showLabel?: boolean
  columns?: number | string
  responsive?: AppFormResponsive
  xGap?: number | string
  yGap?: number | string
}

export interface AppFormProps<T extends object = AppFormRecord> {
  model: T
  fields?: ReadonlyArray<AppFormField<T>>
  groups?: ReadonlyArray<AppFormGroup<T>>
  rules?: FormRules
  layout?: AppFormLayout
  initialValues?: T
  loading?: boolean
  disabled?: boolean
  showActions?: boolean
  showReset?: boolean
  submitText?: string
  resetText?: string
}

export interface AppFormValidationPayload {
  valid: boolean
  errors?: FormValidationError
}

export interface AppFormGroupMutation {
  groupKey: string
  index: number
  value: AppFormRecord
}

export interface AppFormExposed<T extends object = AppFormRecord> {
  validate: () => Promise<boolean>
  submit: (event?: Event) => Promise<boolean>
  reset: () => void
  restoreValidation: () => void
  addGroup: (groupKey: string) => boolean
  removeGroup: (groupKey: string, index: number) => boolean
  getFormInst: () => FormInst | null
  getModel: () => T
}
