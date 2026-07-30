import { computed, ref } from 'vue'
import { darkTheme } from 'naive-ui'

const THEME_STORAGE_KEY = 'fastapi-admin:theme'

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

const darkMode = ref(readStoredTheme())

export const useTheme = () => {
  const isDarkMode = computed(() => darkMode.value)
  const naiveTheme = computed(() => (darkMode.value ? darkTheme : null))

  const toggleTheme = (): void => {
    darkMode.value = !darkMode.value
    persistTheme(darkMode.value)
  }

  return {
    isDarkMode,
    naiveTheme,
    toggleTheme,
  }
}
