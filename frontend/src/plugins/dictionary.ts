import type { Pinia } from 'pinia'
import type { Plugin } from 'vue'

import DictTag from '@/components/DictTag/index.vue'
import { useDict } from '@/hooks/useDict'
import { useDictionaryStore } from '@/stores'
import type { DictionaryCacheService } from '@/types'

export const createDictionaryPlugin = (pinia: Pinia): Plugin => ({
  install: (app) => {
    const store = useDictionaryStore(pinia)
    const service: DictionaryCacheService = {
      get: (dictType) => store.load(dictType),
      refresh: (dictType) => store.load(dictType, true),
      peek: (dictType) => store.peek(dictType),
      remove: (dictType) => store.remove(dictType),
      clear: () => store.clear(),
    }

    app.component('DictTag', DictTag)
    app.config.globalProperties.$dict = service
    app.config.globalProperties.useDict = useDict
  },
})
