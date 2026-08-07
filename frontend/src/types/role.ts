import type { PaginationResult } from './pagination'

export interface RoleOption {
  id: number
  name: string
  code: string
  description: string | null
  status: '0' | '1'
}

export type RolePage = PaginationResult<RoleOption>
