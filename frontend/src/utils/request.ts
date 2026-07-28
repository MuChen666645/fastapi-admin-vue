import { createAlova } from 'alova'
import adapterFetch from 'alova/fetch'
import type { RequestBody } from 'alova'

import { parseApiResponse, type TokenResponse } from '@/types/api'

const requestTimeout = 15_000

export class ApiError extends Error {
  readonly status: number
  readonly code: number | null
  readonly errorCode: string | null

  constructor(
    message: string,
    status: number,
    code: number | null = null,
    errorCode: string | null = null,
  ) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.code = code
    this.errorCode = errorCode
  }
}

interface AuthTransportHandlers {
  getAccessToken: () => string | null
  getRefreshToken: () => string | null
  setTokens: (tokens: TokenResponse) => void
  clearSession: () => void
  refreshTokens: ((refreshToken: string) => Promise<TokenResponse>) | null
}

const authHandlers: AuthTransportHandlers = {
  getAccessToken: () => null,
  getRefreshToken: () => null,
  setTokens: () => undefined,
  clearSession: () => undefined,
  refreshTokens: null,
}

let refreshPromise: Promise<boolean> | null = null

export const configureAuthTransport = (
  handlers: Omit<AuthTransportHandlers, 'refreshTokens'>,
): void => {
  authHandlers.getAccessToken = handlers.getAccessToken
  authHandlers.getRefreshToken = handlers.getRefreshToken
  authHandlers.setTokens = handlers.setTokens
  authHandlers.clearSession = handlers.clearSession
}

export const registerRefreshTokenRequest = (
  refreshTokens: (refreshToken: string) => Promise<TokenResponse>,
): void => {
  authHandlers.refreshTokens = refreshTokens
}

const alova = createAlova({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  requestAdapter: adapterFetch(),
  timeout: requestTimeout,
  // 验证码刷新需要每次都向服务端申请新内容，不能复用相同路径的请求。
  shareRequest: false,
  beforeRequest: (method) => {
    const accessToken = authHandlers.getAccessToken()
    if (accessToken) {
      method.config.headers.Authorization = `Bearer ${accessToken}`
    }
  },
})

const sendRequest = async (path: string, options: RequestOptions): Promise<Response> => {
  const method = alova.Request<Response>({
    url: path,
    method: options.method ?? 'GET',
    data: options.data,
    headers: options.headers,
    timeout: requestTimeout,
  })

  return method.send()
}

const readResponse = async (response: Response) => {
  if (response.status === 204) {
    return { response, payload: { code: 204, message: 'success', data: null } }
  }

  let body: unknown
  try {
    body = await response.json()
  } catch {
    throw new ApiError('服务响应无法解析', response.status)
  }

  try {
    return { response, payload: parseApiResponse(body) }
  } catch {
    throw new ApiError('服务响应格式无效', response.status)
  }
}

const refreshAccessToken = async (): Promise<boolean> => {
  if (!authHandlers.refreshTokens) {
    return false
  }

  if (refreshPromise) {
    return refreshPromise
  }

  const refreshToken = authHandlers.getRefreshToken()
  if (!refreshToken) {
    return false
  }

  refreshPromise = (async () => {
    try {
      const tokens = await authHandlers.refreshTokens?.(refreshToken)
      if (!tokens) {
        throw new ApiError('会话刷新失败', 401)
      }

      authHandlers.setTokens(tokens)
      return true
    } catch {
      authHandlers.clearSession()
      return false
    } finally {
      refreshPromise = null
    }
  })()

  return refreshPromise
}

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'
  data?: RequestBody
  headers?: Record<string, string>
  auth?: boolean
  skipAuthRefresh?: boolean
}

export const requestJson = async <T>(
  path: string,
  options: RequestOptions,
  parseData: (value: unknown) => T,
): Promise<T> => {
  const response = await sendRequest(path, options)
  const { response: responseData, payload } = await readResponse(response)

  if (
    responseData.status === 401 &&
    options.auth !== false &&
    options.skipAuthRefresh !== true &&
    (await refreshAccessToken())
  ) {
    return requestJson(path, { ...options, skipAuthRefresh: true }, parseData)
  }

  if (!responseData.ok || payload.code < 200 || payload.code >= 300) {
    throw new ApiError(
      payload.message || '请求失败',
      responseData.status,
      payload.code,
      payload.error_code ?? null,
    )
  }

  try {
    return parseData(payload.data)
  } catch (error) {
    const message = error instanceof Error ? error.message : '服务数据格式无效'
    throw new ApiError(message, responseData.status, payload.code)
  }
}
