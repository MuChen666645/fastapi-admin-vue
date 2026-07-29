import type { RequestBody } from 'alova'

import type { TokenResponse } from './api'

export interface AuthTransportHandlers {
  getAccessToken: () => string | null
  getRefreshToken: () => string | null
  setTokens: (tokens: TokenResponse) => void
  clearSession: () => void
  refreshTokens: ((refreshToken: string) => Promise<TokenResponse>) | null
}

export interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'
  data?: RequestBody
  headers?: Record<string, string>
  auth?: boolean
  skipAuthRefresh?: boolean
}
