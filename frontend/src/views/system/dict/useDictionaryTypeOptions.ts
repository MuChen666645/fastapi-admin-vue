import { onMounted, ref } from 'vue'

import { fetchDictTypeList } from '@/api'
import type { DictTypeListItem } from '@/types'

const TYPE_PAGE_SIZE = 100

export const useDictionaryTypeOptions = () => {
  const items = ref<DictTypeListItem[]>([])
  const loading = ref(false)
  const error = ref<Error | null>(null)
  let requestVersion = 0

  const load = async (): Promise<DictTypeListItem[] | null> => {
    const currentVersion = requestVersion + 1
    requestVersion = currentVersion
    loading.value = true
    error.value = null

    try {
      const firstPage = await fetchDictTypeList(
        { page: 1, size: TYPE_PAGE_SIZE },
        { name: '', status: null },
      )
      const nextItems = [...firstPage.items]

      for (let page = 2; page <= firstPage.pages; page += 1) {
        const response = await fetchDictTypeList(
          { page, size: TYPE_PAGE_SIZE },
          { name: '', status: null },
        )
        nextItems.push(...response.items)
      }

      if (currentVersion !== requestVersion) {
        return null
      }

      items.value = nextItems
      return nextItems
    } catch (loadError) {
      if (currentVersion === requestVersion) {
        error.value = loadError instanceof Error ? loadError : new Error('字典类型加载失败')
      }
      return null
    } finally {
      if (currentVersion === requestVersion) {
        loading.value = false
      }
    }
  }

  onMounted(() => {
    void load()
  })

  return { error, items, load, loading }
}
