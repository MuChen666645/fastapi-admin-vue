export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number | null
  must_change_password: boolean
}

export interface CaptchaImageResponse {
  captcha_id: string
  image: string
}

export interface LoginCredentials {
  loginType: 'username' | 'phone'
  identifier: string
  password: string
  captcha_id: string
  captcha: string
  mfa_code?: string
}
