import type { DictionaryCacheService, DictionaryUse } from '@/types/dictionary'

declare module 'vue' {
  interface ComponentCustomProperties {
    $dict: DictionaryCacheService
    useDict: DictionaryUse
  }
}

export {}
