import { shallowRef } from 'vue'
import { defineStore } from 'pinia'

import { fetchDictDataByType } from '@/api/dictionary'
import type { DictDataListItem, DictionaryCacheRecord, DictionaryErrorRecord } from '@/types'

export const useDictionaryStore = defineStore('dictionary', () => {
  const cache = shallowRef<DictionaryCacheRecord>({})
  const errors = shallowRef<DictionaryErrorRecord>({})
  const loadingTypes = shallowRef<ReadonlySet<string>>(new Set())
  const pendingRequests = new Map<string, Promise<ReadonlyArray<DictDataListItem>>>()
  const activeRequestIds = new Map<string, number>()
  const cacheVersions = new Map<string, number>()
  let requestSequence = 0

  const hasOwn = (record: object, key: string): boolean =>
    Object.prototype.hasOwnProperty.call(record, key)

  const normalizeType = (dictType: string): string => {
    const normalizedType = dictType.trim()
    if (!normalizedType) {
      throw new Error('字典类型编码不能为空')
    }
    return normalizedType
  }

  const setLoading = (dictType: string, loading: boolean): void => {
    const nextLoadingTypes = new Set(loadingTypes.value)
    if (loading) {
      nextLoadingTypes.add(dictType)
    } else {
      nextLoadingTypes.delete(dictType)
    }
    loadingTypes.value = nextLoadingTypes
  }

  const clearError = (dictType: string): void => {
    if (!hasOwn(errors.value, dictType)) {
      return
    }

    const nextErrors = { ...errors.value }
    delete nextErrors[dictType]
    errors.value = nextErrors
  }

  const peek = (dictType: string): ReadonlyArray<DictDataListItem> | undefined =>
    cache.value[normalizeType(dictType)]

  const getError = (dictType: string): Error | undefined => errors.value[normalizeType(dictType)]

  const isLoading = (dictType: string): boolean => loadingTypes.value.has(normalizeType(dictType))

  const executeLoad = async (
    dictType: string,
    requestId: number,
    cacheVersion: number,
  ): Promise<ReadonlyArray<DictDataListItem>> => {
    setLoading(dictType, true)
    clearError(dictType)

    try {
      const items = await fetchDictDataByType(dictType)
      if ((cacheVersions.get(dictType) ?? 0) === cacheVersion) {
        cache.value = { ...cache.value, [dictType]: items }
      }
      return items
    } catch (error) {
      const requestError = error instanceof Error ? error : new Error('字典数据加载失败')
      if ((cacheVersions.get(dictType) ?? 0) === cacheVersion) {
        errors.value = { ...errors.value, [dictType]: requestError }
      }
      throw requestError
    } finally {
      if (activeRequestIds.get(dictType) === requestId) {
        activeRequestIds.delete(dictType)
        pendingRequests.delete(dictType)
        setLoading(dictType, false)
      }
    }
  }

  const load = (
    dictType: string,
    forceRefresh = false,
  ): Promise<ReadonlyArray<DictDataListItem>> => {
    const normalizedType = normalizeType(dictType)
    if (!forceRefresh && hasOwn(cache.value, normalizedType)) {
      return Promise.resolve(cache.value[normalizedType] ?? [])
    }

    const pendingRequest = pendingRequests.get(normalizedType)
    if (pendingRequest) {
      return pendingRequest
    }

    requestSequence += 1
    const requestId = requestSequence
    const cacheVersion = cacheVersions.get(normalizedType) ?? 0
    const request = executeLoad(normalizedType, requestId, cacheVersion)
    activeRequestIds.set(normalizedType, requestId)
    pendingRequests.set(normalizedType, request)
    return request
  }

  const remove = (dictType: string): void => {
    const normalizedType = normalizeType(dictType)
    cacheVersions.set(normalizedType, (cacheVersions.get(normalizedType) ?? 0) + 1)
    pendingRequests.delete(normalizedType)
    activeRequestIds.delete(normalizedType)

    const nextCache = { ...cache.value }
    delete nextCache[normalizedType]
    cache.value = nextCache
    clearError(normalizedType)
    setLoading(normalizedType, false)
  }

  const clear = (): void => {
    const invalidatedTypes = new Set([
      ...Object.keys(cache.value),
      ...pendingRequests.keys(),
      ...activeRequestIds.keys(),
    ])
    invalidatedTypes.forEach((dictType) => {
      cacheVersions.set(dictType, (cacheVersions.get(dictType) ?? 0) + 1)
    })
    pendingRequests.clear()
    activeRequestIds.clear()
    cache.value = {}
    errors.value = {}
    loadingTypes.value = new Set()
  }

  return { cache, clear, errors, getError, isLoading, load, loadingTypes, peek, remove }
})
