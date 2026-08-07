import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import type { TokenResponse } from '@/types'

import {
  ApiError,
  configureAuthTransport,
  invalidateAuthSession,
  registerAuthSessionExpiredHandler,
  registerRefreshTokenRequest,
  requestJson,
} from '../utils/request'
import { configureRequestMessage } from '../utils/request-feedback'

const createResponse = (status: number, data: unknown): Response =>
  new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })

const tokenResponse: TokenResponse = {
  access_token: 'fresh-access-token',
  refresh_token: 'fresh-refresh-token',
  token_type: 'bearer',
  expires_in: 3600,
  must_change_password: false,
}

describe('request transport', () => {
  let accessToken: string | null
  let refreshToken: string | null

  beforeEach(() => {
    accessToken = 'expired-access-token'
    refreshToken = 'refresh-token'
    configureRequestMessage(null)
    configureAuthTransport({
      getAccessToken: () => accessToken,
      getRefreshToken: () => refreshToken,
      setTokens: (tokens) => {
        accessToken = tokens.access_token
        refreshToken = tokens.refresh_token
      },
      clearSession: () => {
        invalidateAuthSession()
        accessToken = null
        refreshToken = null
      },
    })
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('shares one refresh request and retries concurrent 401 responses', async () => {
    const fetchMock = vi.fn(() => {
      if (accessToken === 'expired-access-token') {
        return Promise.resolve(createResponse(401, { message: 'expired' }))
      }

      return Promise.resolve(createResponse(200, { code: 200, message: 'ok', data: { ok: true } }))
    })
    vi.stubGlobal('fetch', fetchMock)

    const refreshMock = vi.fn(async () => {
      return tokenResponse
    })
    registerRefreshTokenRequest(refreshMock)

    const [first, second] = await Promise.all([
      requestJson('/protected/first', {}, (value) => value),
      requestJson('/protected/second', {}, (value) => value),
    ])

    expect(first).toEqual({ ok: true })
    expect(second).toEqual({ ok: true })
    expect(refreshMock).toHaveBeenCalledOnce()
    expect(fetchMock).toHaveBeenCalledTimes(4)
  })

  it('does not apply a refresh result after the session was invalidated', async () => {
    const fetchMock = vi.fn(() => Promise.resolve(createResponse(401, { message: 'expired' })))
    vi.stubGlobal('fetch', fetchMock)

    let refreshStarted = false
    let resolveRefresh: (tokens: TokenResponse) => void = () => {
      throw new Error('刷新 Promise 尚未初始化')
    }
    registerRefreshTokenRequest(() => {
      refreshStarted = true
      return new Promise((resolve) => {
        resolveRefresh = resolve
      })
    })

    const request = requestJson('/protected', {}, (value) => value)
    await vi.waitFor(() => expect(refreshStarted).toBe(true))

    invalidateAuthSession()
    accessToken = null
    refreshToken = null
    resolveRefresh(tokenResponse)

    await expect(request).rejects.toBeInstanceOf(ApiError)
    expect(accessToken).toBeNull()
  })

  it('clears an expired session and notifies the router when refresh fails', async () => {
    const sessionExpired = vi.fn()
    registerAuthSessionExpiredHandler(sessionExpired)
    registerRefreshTokenRequest(async () => {
      throw new ApiError('refresh failed', 401)
    })
    vi.stubGlobal(
      'fetch',
      vi.fn(() => Promise.resolve(createResponse(401, { message: 'expired' }))),
    )

    await expect(requestJson('/protected', {}, (value) => value)).rejects.toMatchObject({
      status: 401,
    })

    expect(accessToken).toBeNull()
    expect(refreshToken).toBeNull()
    expect(sessionExpired).toHaveBeenCalledOnce()
    registerAuthSessionExpiredHandler(null)
  })

  it('normalizes network failures and sends one Message notification', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(() => Promise.reject(new TypeError('network down'))),
    )
    const showMessage = vi.fn()
    configureRequestMessage(showMessage)

    await expect(requestJson('/protected', {}, (value) => value)).rejects.toMatchObject({
      status: 0,
      message: '网络请求失败，请检查网络连接',
    })
    expect(showMessage).toHaveBeenCalledOnce()
    expect(showMessage).toHaveBeenCalledWith('网络请求失败，请检查网络连接')
  })
})
