import type { RequestBody } from 'alova'

import type { TokenResponse } from './api'

export interface AuthTransportHandlers {
  getAccessToken: () => string | null
  getRefreshToken: () => string | null
  setTokens: (tokens: TokenResponse) => void
  clearSession: () => void
  refreshTokens: ((refreshToken: string) => Promise<TokenResponse>) | null
}

export type AuthSessionExpiredHandler = () => void

export type RequestParameterValue =
  | string
  | number
  | boolean
  | null
  | undefined
  | ReadonlyArray<string | number | boolean | null | undefined>

export type RequestParameters = Record<string, RequestParameterValue>

export interface RequestFileResponse {
  blob: Blob
  filename: string | null
}

export interface RequestOptions<TParameters extends object = object> {
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'
  data?: RequestBody
  params?: TParameters
  headers?: Record<string, string>
  timeout?: number
  auth?: boolean
  skipAuthRefresh?: boolean
  showMessage?: boolean
}

export type RequestMessageHandler = (message: string) => void
