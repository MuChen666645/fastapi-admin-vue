import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

const requestJson = vi.hoisted(() => vi.fn())
const registerRefreshTokenRequest = vi.hoisted(() => vi.fn())

vi.mock('../utils/request', () => ({
  registerRefreshTokenRequest,
  requestJson,
}))

import { fetchCaptcha } from '../api/auth'

describe('认证接口', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  beforeEach(() => {
    requestJson.mockResolvedValue({
      captcha_id: 'captcha-id',
      image: 'data:image/png;base64,captcha',
    })
  })

  it('为每次验证码请求追加时间戳', async () => {
    vi.spyOn(Date, 'now').mockReturnValueOnce(1700000000000).mockReturnValueOnce(1700000001000)

    await fetchCaptcha()
    await fetchCaptcha()

    expect(requestJson.mock.calls[0]?.[0]).toBe('/captcha/image?timestamp=1700000000000')
    expect(requestJson.mock.calls[1]?.[0]).toBe('/captcha/image?timestamp=1700000001000')
  })
})
