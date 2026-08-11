import { computed, onMounted } from 'vue'

import { useDictionaryStore } from '@/stores'
import type { DictDataListItem, DictionaryUse } from '@/types'

export const useDict: DictionaryUse = (...dictTypes) => {
  const store = useDictionaryStore()
  const normalizedTypes = [...new Set(dictTypes.map((dictType) => dictType.trim()))]
  if (normalizedTypes.some((dictType) => !dictType)) {
    throw new Error('字典类型编码不能为空')
  }

  const dictionaries = Object.fromEntries(
    normalizedTypes.map((dictType) => [
      dictType,
      computed<ReadonlyArray<DictDataListItem>>(() => store.peek(dictType) ?? []),
    ]),
  )

  onMounted(() => {
    void Promise.allSettled(normalizedTypes.map((dictType) => store.load(dictType)))
  })

  return Object.freeze(dictionaries)
}
