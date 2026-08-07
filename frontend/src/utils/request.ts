import { createAlova } from 'alova'
import adapterFetch from 'alova/fetch'

import type {
  AuthSessionExpiredHandler,
  AuthTransportHandlers,
  RequestOptions,
  TokenResponse,
} from '@/types'
import { parseApiResponse } from '@/utils/guards/api'
import { showRequestMessage } from '@/utils/request-feedback'

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

const authHandlers: AuthTransportHandlers = {
  getAccessToken: () => null,
  getRefreshToken: () => null,
  setTokens: () => undefined,
  clearSession: () => undefined,
  refreshTokens: null,
}

let authSessionExpiredHandler: AuthSessionExpiredHandler | null = null
let refreshPromise: Promise<boolean> | null = null
let authSessionVersion = 0

export const configureAuthTransport = (
  handlers: Omit<AuthTransportHandlers, 'refreshTokens'>,
): void => {
  authSessionVersion += 1
  refreshPromise = null
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

export const registerAuthSessionExpiredHandler = (
  handler: AuthSessionExpiredHandler | null,
): void => {
  authSessionExpiredHandler = handler
}

export const invalidateAuthSession = (): void => {
  authSessionVersion += 1
  refreshPromise = null
}

const expireAuthSession = (): void => {
  const hasSession =
    authHandlers.getAccessToken() !== null || authHandlers.getRefreshToken() !== null
  if (!hasSession) {
    return
  }

  authHandlers.clearSession()
  authSessionExpiredHandler?.()
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
    cacheFor: 0,
  })

  return method.send()
}

const getHttpErrorMessage = (status: number): string => {
  if (status === 401) {
    return '登录状态已失效，请重新登录'
  }

  if (status === 403) {
    return '没有权限访问此资源'
  }

  if (status === 404) {
    return '请求资源不存在'
  }

  if (status >= 500) {
    return '服务暂时不可用，请稍后重试'
  }

  return '请求失败，请稍后重试'
}

const createHttpErrorPayload = (status: number) => ({
  code: status,
  message: getHttpErrorMessage(status),
  data: null,
})

const readResponse = async (response: Response) => {
  if (response.status === 204) {
    return { response, payload: { code: 204, message: 'success', data: null } }
  }

  let body: unknown
  try {
    body = await response.json()
  } catch {
    if (!response.ok) {
      return { response, payload: createHttpErrorPayload(response.status) }
    }

    throw new ApiError('服务响应无法解析', response.status)
  }

  try {
    return { response, payload: parseApiResponse(body) }
  } catch {
    if (!response.ok) {
      return { response, payload: createHttpErrorPayload(response.status) }
    }

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

  const sessionVersion = authSessionVersion
  let pendingRefresh: Promise<boolean> | null = null
  pendingRefresh = (async () => {
    try {
      const tokens = await authHandlers.refreshTokens?.(refreshToken)
      if (!tokens) {
        throw new ApiError('会话刷新失败', 401)
      }

      if (
        sessionVersion !== authSessionVersion ||
        authHandlers.getRefreshToken() !== refreshToken
      ) {
        return false
      }

      authHandlers.setTokens(tokens)
      return true
    } catch {
      if (sessionVersion === authSessionVersion) {
        expireAuthSession()
      }

      return false
    } finally {
      if (refreshPromise === pendingRefresh) {
        refreshPromise = null
      }
    }
  })()
  refreshPromise = pendingRefresh

  return refreshPromise
}

const executeRequest = async <T>(
  path: string,
  options: RequestOptions,
  parseData: (value: unknown) => T,
): Promise<T> => {
  const response = await sendRequest(path, options)
  const { response: responseData, payload } = await readResponse(response)

  const unauthorized = responseData.status === 401 || payload.code === 401
  if (
    unauthorized &&
    options.auth !== false &&
    options.skipAuthRefresh !== true &&
    (await refreshAccessToken())
  ) {
    return executeRequest(path, { ...options, skipAuthRefresh: true }, parseData)
  }

  if (unauthorized && options.auth !== false) {
    expireAuthSession()
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

const normalizeRequestError = (error: unknown): ApiError => {
  if (error instanceof ApiError) {
    return error
  }

  return new ApiError('网络请求失败，请检查网络连接', 0)
}

export const requestJson = async <T>(
  path: string,
  options: RequestOptions,
  parseData: (value: unknown) => T,
): Promise<T> => {
  try {
    return await executeRequest(path, options, parseData)
  } catch (error) {
    const normalizedError = normalizeRequestError(error)
    if (options.showMessage !== false) {
      showRequestMessage(normalizedError.message)
    }

    throw normalizedError
  }
}
