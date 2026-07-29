export interface RememberedLogin {
  identifier: string
  password: string
}

const LOGIN_PREFERENCES_KEY = 'fastapi-admin:remembered-login'

const getStorage = (): Storage | null => {
  if (typeof window === 'undefined') {
    return null
  }

  try {
    return window.localStorage
  } catch {
    return null
  }
}

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === 'object' && value !== null

const isValidRememberedLogin = (value: unknown): value is RememberedLogin => {
  if (!isRecord(value)) {
    return false
  }

  return (
    typeof value.identifier === 'string' &&
    value.identifier.length > 0 &&
    typeof value.password === 'string' &&
    value.password.length > 0
  )
}

export const getRememberedLogin = (): RememberedLogin | null => {
  const storage = getStorage()
  if (!storage) {
    return null
  }

  try {
    const rawValue = storage.getItem(LOGIN_PREFERENCES_KEY)
    if (!rawValue) {
      return null
    }

    const parsedValue: unknown = JSON.parse(rawValue)
    return isValidRememberedLogin(parsedValue) ? parsedValue : null
  } catch {
    return null
  }
}

export const saveRememberedLogin = (credentials: RememberedLogin): void => {
  const storage = getStorage()
  if (!storage) {
    return
  }

  try {
    storage.setItem(LOGIN_PREFERENCES_KEY, JSON.stringify(credentials))
  } catch {
    // 缓存不可用时继续完成登录，不让偏好设置阻断认证流程。
  }
}

export const clearRememberedLogin = (): void => {
  const storage = getStorage()
  if (!storage) {
    return
  }

  try {
    storage.removeItem(LOGIN_PREFERENCES_KEY)
  } catch {
    // 缓存不可用时忽略清理失败。
  }
}
