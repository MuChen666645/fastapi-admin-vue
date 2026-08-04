import { watch } from 'vue'
import { useRoute } from 'vue-router'

import { usePreferencesStore } from '@/stores'
import { translateRouteTitle } from '@/utils'

export const useDocumentTitle = (): void => {
  const route = useRoute()
  const preferences = usePreferencesStore()
  const appTitle = import.meta.env.VITE_APP_TITLE || 'FastAPI Admin'

  watch(
    () => [route.meta.title, preferences.dynamicTitle, preferences.language] as const,
    ([title, dynamicTitle, language]) => {
      if (typeof document === 'undefined') {
        return
      }

      document.title =
        dynamicTitle && typeof title === 'string'
          ? `${translateRouteTitle(title, language)} | ${appTitle}`
          : appTitle
    },
    { immediate: true },
  )
}
