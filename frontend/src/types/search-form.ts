import type { FormRules } from 'naive-ui'

import type {
  AppFormExposed,
  AppFormField,
  AppFormLayout,
  AppFormRecord,
  AppFormValidationPayload,
} from './form'

export type AppSearchFormActionAlign = 'start' | 'center' | 'end'

export interface AppSearchFormLayout extends AppFormLayout {
  actionAlign?: AppSearchFormActionAlign
}

export interface AppSearchFormProps<T extends object = AppFormRecord> {
  model: T
  fields?: ReadonlyArray<AppFormField<T>>
  rules?: FormRules
  layout?: AppSearchFormLayout
  initialValues?: T
  loading?: boolean
  disabled?: boolean
  collapsed?: boolean
  defaultCollapsed?: boolean
  collapsedFields?: number
  showToggle?: boolean
  showSearch?: boolean
  showReset?: boolean
  searchOnEnter?: boolean
  searchText?: string
  resetText?: string
  expandText?: string
  collapseText?: string
}

export interface AppSearchFormExposed<T extends object = AppFormRecord> extends Pick<
  AppFormExposed<T>,
  'validate' | 'restoreValidation' | 'getFormInst' | 'getModel'
> {
  search: (event?: Event) => Promise<boolean>
  reset: () => void
  toggle: () => boolean
  isCollapsed: () => boolean
}

export type AppSearchFormValidationPayload = AppFormValidationPayload
