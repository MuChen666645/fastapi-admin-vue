import { computed, ref } from 'vue'
import { darkTheme } from 'naive-ui'

import { usePreferencesStore } from '@/stores'

const THEME_STORAGE_KEY = 'fastapi-admin:theme'
const THEME_TRANSITION_CLASS = 'app-theme-changing'

let themeTransitionTimer: number | undefined

const readStoredTheme = (): boolean => {
  if (typeof window === 'undefined') {
    return false
  }

  try {
    return window.localStorage.getItem(THEME_STORAGE_KEY) === 'dark'
  } catch {
    return false
  }
}

const persistTheme = (isDark: boolean): void => {
  if (typeof window === 'undefined') {
    return
  }

  try {
    window.localStorage.setItem(THEME_STORAGE_KEY, isDark ? 'dark' : 'light')
  } catch {
    // 缓存不可用时保留当前页面主题，不影响主题切换。
  }
}

const readSystemTheme = (): boolean =>
  typeof window !== 'undefined' &&
  typeof window.matchMedia === 'function' &&
  window.matchMedia('(prefers-color-scheme: dark)').matches

const startThemeTransition = (): void => {
  if (typeof window === 'undefined') {
    return
  }

  document.documentElement.classList.add(THEME_TRANSITION_CLASS)

  if (themeTransitionTimer !== undefined) {
    window.clearTimeout(themeTransitionTimer)
  }

  themeTransitionTimer = window.setTimeout(() => {
    document.documentElement.classList.remove(THEME_TRANSITION_CLASS)
    themeTransitionTimer = undefined
  }, 0)
}

const systemDarkMode = ref(readSystemTheme())
let systemThemeListenerRegistered = false

const registerSystemThemeListener = (): void => {
  if (
    systemThemeListenerRegistered ||
    typeof window === 'undefined' ||
    typeof window.matchMedia !== 'function'
  ) {
    return
  }

  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
  const handleChange = (event: MediaQueryListEvent): void => {
    systemDarkMode.value = event.matches
  }

  mediaQuery.addEventListener?.('change', handleChange)
  systemThemeListenerRegistered = true
}

export const useTheme = () => {
  const preferences = usePreferencesStore()
  registerSystemThemeListener()

  if (
    typeof window !== 'undefined' &&
    !window.localStorage.getItem('preferences') &&
    readStoredTheme()
  ) {
    preferences.themeMode = 'dark'
  }

  const isDarkMode = computed(() => {
    if (preferences.themeMode === 'dark') {
      return true
    }

    if (preferences.themeMode === 'system') {
      return systemDarkMode.value
    }

    return false
  })
  const naiveTheme = computed(() => (isDarkMode.value ? darkTheme : null))

  const toggleTheme = (): void => {
    startThemeTransition()
    preferences.themeMode = isDarkMode.value ? 'light' : 'dark'
    persistTheme(isDarkMode.value)
  }

  return {
    isDarkMode,
    naiveTheme,
    toggleTheme,
  }
}
