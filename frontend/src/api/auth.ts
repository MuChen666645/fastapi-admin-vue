import {
  parseCaptchaImageResponse,
  parseCurrentUserResponse,
  parseTokenResponse,
  parseUserRoutes,
  type CaptchaImageResponse,
  type CurrentUserResponse,
  type LoginCredentials,
  type TokenResponse,
  type UserRoute,
} from '@/types/api'

import { registerRefreshTokenRequest, requestJson } from '@/utils/request'

const createLoginBody = (credentials: LoginCredentials): URLSearchParams => {
  const body = new URLSearchParams()
  body.set('captcha_id', credentials.captcha_id)
  body.set('captcha', credentials.captcha)
  body.set(credentials.loginType, credentials.identifier)
  body.set('password', credentials.password)
  if (credentials.mfa_code) {
    body.set('mfa_code', credentials.mfa_code)
  }
  return body
}

export const fetchCaptcha = (): Promise<CaptchaImageResponse> =>
  requestJson(`/captcha/image?timestamp=${Date.now()}`, {}, parseCaptchaImageResponse)

export const login = (credentials: LoginCredentials): Promise<TokenResponse> =>
  requestJson(
    `/user/login/${credentials.loginType}`,
    {
      method: 'POST',
      data: createLoginBody(credentials),
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      auth: false,
      skipAuthRefresh: true,
    },
    parseTokenResponse,
  )

export const refreshTokens = (refreshToken: string): Promise<TokenResponse> =>
  requestJson(
    '/user/token/refresh',
    {
      method: 'POST',
      data: { refresh_token: refreshToken },
      auth: false,
      skipAuthRefresh: true,
    },
    parseTokenResponse,
  )

registerRefreshTokenRequest(refreshTokens)

export const fetchCurrentUser = (): Promise<CurrentUserResponse> =>
  requestJson('/user/info', {}, parseCurrentUserResponse)

export const fetchUserRoutes = (): Promise<UserRoute[]> =>
  requestJson('/user/routes', {}, parseUserRoutes)

export const changeCurrentPassword = (oldPassword: string, newPassword: string): Promise<null> =>
  requestJson(
    '/user/me/password',
    {
      method: 'PUT',
      data: { old_password: oldPassword, new_password: newPassword },
    },
    () => null,
  )

export const logout = (): Promise<null> =>
  requestJson('/user/logout', { method: 'POST' }, () => null)
