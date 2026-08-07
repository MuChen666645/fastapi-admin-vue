import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

const authApi = vi.hoisted(() => ({
  changeCurrentPassword: vi.fn(),
  fetchCurrentUser: vi.fn(),
  fetchUserRoutes: vi.fn(),
  login: vi.fn(),
  logout: vi.fn(),
  refreshTokens: vi.fn(),
}))

vi.mock('../api', () => authApi)

import { useAuthStore } from '../stores'

describe('auth store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('skips protected session requests when password change is required', async () => {
    authApi.login.mockResolvedValue({
      access_token: 'access-token',
      refresh_token: 'refresh-token',
      token_type: 'bearer',
      expires_in: 7200,
      must_change_password: true,
    })

    const auth = useAuthStore()

    await auth.signIn(
      {
        loginType: 'username',
        identifier: 'admin',
        password: 'Old-password1!',
        captcha_id: 'captcha-id',
        captcha: '1234',
      },
      false,
    )

    expect(auth.status).toBe('password-change-required')
    expect(authApi.fetchCurrentUser).not.toHaveBeenCalled()
    expect(authApi.fetchUserRoutes).not.toHaveBeenCalled()
  })

  it('reuses an initialized session without issuing duplicate requests', async () => {
    authApi.login.mockResolvedValue({
      access_token: 'access-token',
      refresh_token: 'refresh-token',
      token_type: 'bearer',
      expires_in: 7200,
      must_change_password: false,
    })
    authApi.fetchCurrentUser.mockResolvedValue({
      posts: [],
      user: {
        id: 1,
        username: 'admin',
        nickname: null,
        email: null,
        phone: null,
        avatar: null,
        status: '1',
      },
      roles: [],
      permissions: [],
    })
    authApi.fetchUserRoutes.mockResolvedValue([
      {
        path: 'home',
        name: 'home',
        component: 'home/index',
        redirect: null,
        hidden: false,
        meta: {
          title: 'Home',
          menuType: 'C',
          icon: null,
          noCache: false,
          link: null,
        },
        children: [],
      },
    ])

    const auth = useAuthStore()
    await auth.signIn(
      {
        loginType: 'username',
        identifier: 'admin',
        password: 'Old-password1!',
        captcha_id: 'captcha-id',
        captcha: '1234',
      },
      false,
    )

    expect(await auth.initializeSession()).toBe(true)
    expect(authApi.fetchCurrentUser).toHaveBeenCalledTimes(1)
    expect(authApi.fetchUserRoutes).toHaveBeenCalledTimes(1)
  })

  it('clears the session when the user has no accessible routes', async () => {
    authApi.fetchCurrentUser.mockResolvedValue({
      posts: [],
      user: {
        id: 1,
        username: 'route-less-user',
        nickname: null,
        email: null,
        phone: null,
        avatar: null,
        status: '1',
      },
      roles: [],
      permissions: [],
    })
    authApi.fetchUserRoutes.mockResolvedValue([])

    const auth = useAuthStore()
    auth.applyTokens({
      access_token: 'access-token',
      refresh_token: 'refresh-token',
      token_type: 'bearer',
      expires_in: 7200,
      must_change_password: false,
    })

    expect(await auth.initializeSession()).toBe(false)
    expect(auth.accessToken).toBeNull()
    expect(auth.refreshToken).toBeNull()
    expect(auth.status).toBe('signed-out')
  })

  it('retries session requests after an initialization failure', async () => {
    authApi.fetchCurrentUser
      .mockRejectedValueOnce(new Error('temporary failure'))
      .mockResolvedValueOnce({
        posts: [],
        user: {
          id: 1,
          username: 'admin',
          nickname: null,
          email: null,
          phone: null,
          avatar: null,
          status: '1',
        },
        roles: [],
        permissions: [],
      })
    authApi.fetchUserRoutes.mockResolvedValue([
      {
        path: 'home',
        name: 'home',
        component: 'home/index',
        redirect: null,
        hidden: false,
        meta: {
          title: 'Home',
          menuType: 'C',
          icon: null,
          noCache: false,
          link: null,
        },
        children: [],
      },
    ])

    const auth = useAuthStore()
    auth.applyTokens({
      access_token: 'access-token',
      refresh_token: 'refresh-token',
      token_type: 'bearer',
      expires_in: 7200,
      must_change_password: false,
    })

    expect(await auth.initializeSession()).toBe(false)
    expect(await auth.initializeSession()).toBe(true)
    expect(authApi.fetchCurrentUser).toHaveBeenCalledTimes(2)
  })
})
