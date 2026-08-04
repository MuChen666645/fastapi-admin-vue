import { computed, ref } from 'vue'
import { getActivePinia } from 'pinia'

import { usePreferencesStore } from '@/stores'
import { translations } from '@/utils'

import type { PreferenceLanguage, TranslationKey } from '@/types'

export const useLocale = () => {
  const activePinia = getActivePinia()
  const preferences = activePinia ? usePreferencesStore(activePinia) : null
  const language = preferences
    ? computed(() => preferences.language)
    : ref<PreferenceLanguage>('zh-CN')
  const t = (key: TranslationKey): string => translations[language.value][key]

  return { language, t }
}
