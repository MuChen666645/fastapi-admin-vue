import { beforeEach, describe, expect, it } from 'vitest'

import {
  clearRememberedLogin,
  getRememberedLogin,
  saveRememberedLogin,
} from '../utils/loginPreferences'

describe('登录偏好缓存', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('保存并读取记住我的登录凭据', () => {
    const credentials = { identifier: 'admin', password: 'password' }

    saveRememberedLogin(credentials)

    expect(getRememberedLogin()).toEqual(credentials)
  })

  it('忽略无效缓存并支持清理', () => {
    localStorage.setItem('fastapi-admin:remembered-login', '{invalid')
    expect(getRememberedLogin()).toBeNull()

    saveRememberedLogin({ identifier: 'admin', password: 'password' })
    clearRememberedLogin()

    expect(getRememberedLogin()).toBeNull()
  })
})
