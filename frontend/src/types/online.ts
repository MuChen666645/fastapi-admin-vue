import type { PaginationRequest, PaginationResult } from './pagination'

export interface OnlineSession {
  token_id: string
  user_id: number | string
  username: string | null
  ip_address: string | null
  user_agent: string | null
  login_time: string | null
  expire_time: string
}

export interface OnlineSessionFilters {
  [key: string]: unknown
  username: string
  ip_address: string
}

export type OnlineSessionListQuery = PaginationRequest

export type OnlineSessionPage = PaginationResult<OnlineSession>

export interface ForceLogoutUserResult {
  user_id: number
  revoked_token_count: number
}

export interface OnlineActionPermissions {
  list: boolean
  forceLogout: boolean
}

export interface OnlineSearchPanelProps {
  model: OnlineSessionFilters
  initialValues: OnlineSessionFilters
  loading: boolean
}

export interface OnlineSessionTableProps {
  data: OnlineSession[]
  loading: boolean
  forceLogoutAllowed: boolean
  revokingAction: string | null
}
