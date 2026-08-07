import type { PaginationResult } from './pagination'

export interface DepartmentOption {
  dept_id: number
  dept_name: string
  status: '0' | '1'
  children: DepartmentOption[]
}

export interface DepartmentCascaderOption {
  label: string
  value: number
  disabled?: boolean
  children?: DepartmentCascaderOption[]
}

export interface PostOption {
  post_id: number
  post_code: string
  post_name: string
  status: '0' | '1'
}

export type PostPage = PaginationResult<PostOption>
