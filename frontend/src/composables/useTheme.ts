import { computed, ref } from 'vue'
import { darkTheme } from 'naive-ui'

const darkMode = ref(false)

export const useTheme = () => {
  const isDarkMode = computed(() => darkMode.value)
  const naiveTheme = computed(() => (darkMode.value ? darkTheme : null))

  const toggleTheme = (): void => {
    darkMode.value = !darkMode.value
  }

  return {
    isDarkMode,
    naiveTheme,
    toggleTheme,
  }
}
