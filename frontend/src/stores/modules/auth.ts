import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import 'pinia-plugin-persistedstate'

import {
  changeCurrentPassword,
  fetchCurrentUser,
  fetchUserRoutes,
  login,
  logout,
  refreshTokens,
} from '@/api'
import type {
  AuthStatus,
  CurrentUserResponse,
  LoginCredentials,
  TokenResponse,
  UserRoute,
} from '@/types'
import { ApiError, configureAuthTransport } from '@/utils/request'

export const useAuthStore = defineStore(
  'auth',
  () => {
    const status = ref<AuthStatus>('signed-out')
    const accessToken = ref<string | null>(null)
    const refreshToken = ref<string | null>(null)
    const rememberedUsername = ref('')
    const mustChangePassword = ref(false)
    const currentUser = ref<CurrentUserResponse | null>(null)
    const routes = ref<UserRoute[]>([])
    const permissions = ref<string[]>([])
    const sessionError = ref<Error | null>(null)
    let initializationPromise: Promise<boolean> | null = null

    const hasSession = computed(() => accessToken.value !== null || refreshToken.value !== null)
    const isAuthenticated = computed(
      () => accessToken.value !== null && status.value === 'authenticated',
    )
    const displayName = computed(
      () => currentUser.value?.user.nickname || currentUser.value?.user.username || '鐢ㄦ埛',
    )

    const applyTokens = (tokens: TokenResponse): void => {
      accessToken.value = tokens.access_token
      refreshToken.value = tokens.refresh_token
      mustChangePassword.value = tokens.must_change_password
      if (tokens.must_change_password) {
        status.value = 'password-change-required'
      }
    }

    const clearSession = (): void => {
      accessToken.value = null
      refreshToken.value = null
      mustChangePassword.value = false
      currentUser.value = null
      routes.value = []
      permissions.value = []
      status.value = 'signed-out'
    }

    configureAuthTransport({
      getAccessToken: () => accessToken.value,
      getRefreshToken: () => refreshToken.value,
      setTokens: applyTokens,
      clearSession,
    })

    const loadSession = async (): Promise<boolean> => {
      status.value = 'initializing'
      sessionError.value = null

      if (!accessToken.value) {
        const persistedRefreshToken = refreshToken.value
        if (!persistedRefreshToken) {
          status.value = 'signed-out'
          return false
        }

        try {
          applyTokens(await refreshTokens(persistedRefreshToken))
        } catch (error) {
          sessionError.value = error instanceof Error ? error : new Error('浼氳瘽鍒锋柊澶辫触')
          clearSession()
          return false
        }
      }

      try {
        if (mustChangePassword.value) {
          currentUser.value = null
          routes.value = []
          permissions.value = []
          status.value = 'password-change-required'
          return true
        }

        currentUser.value = await fetchCurrentUser()
        permissions.value = currentUser.value.permissions

        routes.value = await fetchUserRoutes()
        status.value = 'authenticated'
        return true
      } catch (error) {
        sessionError.value = error instanceof Error ? error : new Error('浼氳瘽鍒濆鍖栧け璐?')
        if (error instanceof ApiError && error.status === 401) {
          clearSession()
        } else {
          status.value = 'failed'
        }
        return false
      }
    }

    const initializeSession = async (): Promise<boolean> => {
      if (status.value === 'authenticated' && currentUser.value) {
        return true
      }

      if (status.value === 'password-change-required' && mustChangePassword.value) {
        return true
      }

      if (initializationPromise) {
        return initializationPromise
      }

      initializationPromise = loadSession()
      try {
        return await initializationPromise
      } finally {
        initializationPromise = null
      }
    }

    const signIn = async (
      credentials: LoginCredentials,
      rememberUsername: boolean,
    ): Promise<void> => {
      status.value = 'initializing'
      sessionError.value = null
      const tokens = await login(credentials)
      applyTokens(tokens)
      rememberedUsername.value = rememberUsername ? credentials.identifier : ''

      const initialized = await initializeSession()
      if (!initialized) {
        const initializationError = sessionError.value
        clearSession()
        throw initializationError ?? new Error('鐧诲綍鍚庢棤娉曞垵濮嬪寲浼氳瘽')
      }
    }

    const updatePassword = async (oldPassword: string, newPassword: string): Promise<void> => {
      await changeCurrentPassword(oldPassword, newPassword)
      mustChangePassword.value = false
      const initialized = await initializeSession()
      if (!initialized) {
        throw new Error('瀵嗙爜宸蹭慨鏀癸紝浣嗘棤娉曞姞杞界敤鎴疯彍鍗?')
      }
    }

    const signOut = async (): Promise<void> => {
      try {
        if (accessToken.value) {
          await logout()
        }
      } finally {
        clearSession()
      }
    }

    return {
      status,
      accessToken,
      refreshToken,
      rememberedUsername,
      mustChangePassword,
      currentUser,
      routes,
      permissions,
      hasSession,
      isAuthenticated,
      displayName,
      applyTokens,
      clearSession,
      initializeSession,
      signIn,
      updatePassword,
      signOut,
    }
  },
  {
    persist: {
      storage: sessionStorage,
      pick: ['refreshToken', 'rememberedUsername'],
    },
  },
)
