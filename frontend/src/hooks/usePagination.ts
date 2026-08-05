import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

import type {
  PaginationBinding,
  PaginationFetcher,
  PaginationOptions,
  PaginationRequest,
  PaginationResetOptions,
  PaginationResult,
} from '@/types'

const DEFAULT_PAGE = 1
const DEFAULT_PAGE_SIZE = 20
const MAX_PAGE_SIZE = 100
const DEFAULT_PAGE_SIZES = [10, 20, 50, 100]

const normalizeInteger = (value: number | undefined, fallback: number, minimum: number): number => {
  if (typeof value !== 'number' || !Number.isFinite(value)) {
    return fallback
  }

  return Math.max(minimum, Math.trunc(value))
}

const normalizePageSize = (value: number | undefined, fallback: number): number =>
  Math.min(MAX_PAGE_SIZE, normalizeInteger(value, fallback, 1))

const normalizePageSizes = (values: readonly number[], initialPageSize: number): number[] => {
  const pageSizes = values
    .filter((value) => Number.isFinite(value))
    .map((value) => normalizePageSize(value, initialPageSize))
    .filter((value, index, source) => source.indexOf(value) === index)

  if (pageSizes.length === 0 || !pageSizes.includes(initialPageSize)) {
    pageSizes.push(initialPageSize)
  }

  return pageSizes
}

const toError = (value: unknown): Error =>
  value instanceof Error ? value : new Error('分页请求失败')

export const usePagination = <T>(
  fetchPage: PaginationFetcher<T>,
  options: PaginationOptions = {},
) => {
  const initialPage = normalizeInteger(options.initialPage, DEFAULT_PAGE, 1)
  const initialPageSize = normalizePageSize(options.initialPageSize, DEFAULT_PAGE_SIZE)
  const pageSizes = normalizePageSizes(options.pageSizes ?? DEFAULT_PAGE_SIZES, initialPageSize)

  const page = ref(initialPage)
  const pageSize = ref(initialPageSize)
  const items = ref<T[]>([])
  const total = ref(0)
  const loading = ref(false)
  const error = ref<Error | null>(null)
  const requestVersion = ref(0)

  const pageCount = computed(() => Math.ceil(total.value / pageSize.value))
  const params = computed<PaginationRequest>(() => ({
    page: page.value,
    size: pageSize.value,
  }))

  const loadPage = async (correctOutOfRangePage = true): Promise<PaginationResult<T> | null> => {
    const currentVersion = requestVersion.value + 1
    requestVersion.value = currentVersion
    const requestParams = { ...params.value }
    loading.value = true
    error.value = null

    try {
      const response = await fetchPage(requestParams)
      if (currentVersion !== requestVersion.value) {
        return null
      }

      const responsePageSize = normalizePageSize(response.size, requestParams.size)
      const responseTotal = Math.max(0, Math.trunc(response.total))
      const responsePageCount = Math.ceil(responseTotal / responsePageSize)
      const responsePage = normalizeInteger(response.page, requestParams.page, 1)

      pageSize.value = responsePageSize
      total.value = responseTotal

      if (
        correctOutOfRangePage &&
        responseTotal > 0 &&
        requestParams.page > responsePageCount &&
        response.items.length === 0
      ) {
        page.value = responsePageCount
        return loadPage(false)
      }

      items.value = response.items
      page.value = responseTotal === 0 ? DEFAULT_PAGE : Math.min(responsePage, responsePageCount)
      return response
    } catch (requestError) {
      if (currentVersion === requestVersion.value) {
        error.value = toError(requestError)
      }
      return null
    } finally {
      if (currentVersion === requestVersion.value) {
        loading.value = false
      }
    }
  }

  const load = (): Promise<PaginationResult<T> | null> => loadPage()

  const handlePageChange = (nextPage: number): void => {
    const normalizedPage = normalizeInteger(nextPage, page.value, 1)
    if (normalizedPage === page.value) {
      return
    }

    page.value = normalizedPage
    void load()
  }

  const handlePageSizeChange = (nextPageSize: number): void => {
    const normalizedPageSize = normalizePageSize(nextPageSize, pageSize.value)
    const shouldLoad = page.value !== DEFAULT_PAGE || pageSize.value !== normalizedPageSize

    page.value = DEFAULT_PAGE
    pageSize.value = normalizedPageSize
    if (shouldLoad) {
      void load()
    }
  }

  const reset = async (
    resetOptions: PaginationResetOptions = {},
  ): Promise<PaginationResult<T> | null> => {
    page.value = initialPage
    pageSize.value = initialPageSize
    error.value = null

    if (resetOptions.reload === false) {
      requestVersion.value += 1
      loading.value = false
      return null
    }

    return load()
  }

  const pagination = computed<PaginationBinding>(() => ({
    page: page.value,
    pageSize: pageSize.value,
    itemCount: total.value,
    pageSizes,
    showSizePicker: pageSizes.length > 0,
    disabled: loading.value,
    'onUpdate:page': handlePageChange,
    'onUpdate:pageSize': handlePageSizeChange,
  }))

  onMounted(() => {
    if (options.immediate !== false) {
      void load()
    }
  })

  onBeforeUnmount(() => {
    requestVersion.value += 1
  })

  return {
    items,
    data: items,
    page,
    pageSize,
    total,
    pageCount,
    params,
    loading,
    error,
    pagination,
    load,
    reload: load,
    refresh: load,
    reset,
    handlePageChange,
    handlePageSizeChange,
  }
}
