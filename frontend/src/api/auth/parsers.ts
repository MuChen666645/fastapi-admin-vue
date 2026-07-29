import type { CaptchaImageResponse, TokenResponse } from '@/types'
import { isRecord, readNumber, readString, requireBoolean, requireString } from '@/utils/guards/api'

export const parseTokenResponse = (value: unknown): TokenResponse => {
  if (!isRecord(value)) {
    throw new Error('令牌响应无效')
  }

  return {
    access_token: requireString(value.access_token, 'access_token'),
    refresh_token: requireString(value.refresh_token, 'refresh_token'),
    token_type: readString(value.token_type, 'bearer') ?? 'bearer',
    expires_in: readNumber(value.expires_in),
    must_change_password: requireBoolean(value.must_change_password, 'must_change_password'),
  }
}

export const parseCaptchaImageResponse = (value: unknown): CaptchaImageResponse => {
  if (!isRecord(value)) {
    throw new Error('验证码响应无效')
  }

  return {
    captcha_id: requireString(value.captcha_id, 'captcha_id'),
    image: requireString(value.image, 'image'),
  }
}
