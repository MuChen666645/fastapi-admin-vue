import type { PaginationProps as NaivePaginationProps } from 'naive-ui'

export interface PaginationRequest {
  page: number
  size: number
}

export interface PaginationResult<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

export type PaginationFetcher<T> = (params: PaginationRequest) => Promise<PaginationResult<T>>

export interface PaginationOptions {
  initialPage?: number
  initialPageSize?: number
  pageSizes?: readonly number[]
  immediate?: boolean
}

export interface PaginationResetOptions {
  reload?: boolean
}

export type PaginationBinding = Pick<
  NaivePaginationProps,
  | 'page'
  | 'pageSize'
  | 'itemCount'
  | 'pageSizes'
  | 'showSizePicker'
  | 'disabled'
  | 'onUpdate:page'
  | 'onUpdate:pageSize'
>
