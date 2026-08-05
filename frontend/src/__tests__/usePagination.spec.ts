import { flushPromises, mount } from '@vue/test-utils'
import { defineComponent, nextTick } from 'vue'
import { describe, expect, it, vi } from 'vitest'

import { usePagination } from '@/hooks'
import type { PaginationFetcher, PaginationResult } from '@/types'

type TestRecord = { id: number }

const createPage = (
  page: number,
  size: number,
  items: TestRecord[],
  total: number,
): PaginationResult<TestRecord> => ({
  items,
  total,
  page,
  size,
  pages: Math.ceil(total / size),
})

describe('usePagination', () => {
  it('loads the backend page contract and exposes Naive UI bindings', async () => {
    const fetchPage = vi
      .fn<PaginationFetcher<TestRecord>>()
      .mockResolvedValue(createPage(1, 20, [{ id: 1 }], 41))
    let paginationState: ReturnType<typeof usePagination<TestRecord>> | undefined
    const wrapper = mount(
      defineComponent({
        setup() {
          paginationState = usePagination(fetchPage, { immediate: false })
          return paginationState
        },
        template: '<div />',
      }),
    )

    await paginationState?.load()

    expect(fetchPage).toHaveBeenCalledWith({ page: 1, size: 20 })
    expect(paginationState?.items.value).toEqual([{ id: 1 }])
    expect(paginationState?.data).toBe(paginationState?.items)
    expect(paginationState?.total.value).toBe(41)
    expect(paginationState?.pageCount.value).toBe(3)
    expect(paginationState?.pagination.value).toMatchObject({
      page: 1,
      pageSize: 20,
      itemCount: 41,
      pageSizes: [10, 20, 50, 100],
      showSizePicker: true,
      disabled: false,
    })

    wrapper.unmount()
  })

  it('changes page and page size through Naive UI handlers', async () => {
    const fetchPage = vi
      .fn<PaginationFetcher<TestRecord>>()
      .mockImplementation(async (params) =>
        createPage(params.page, params.size, [{ id: params.page }], 100),
      )
    let paginationState: ReturnType<typeof usePagination<TestRecord>> | undefined
    const wrapper = mount(
      defineComponent({
        setup() {
          paginationState = usePagination(fetchPage, { immediate: false })
          return paginationState
        },
        template: '<div />',
      }),
    )

    await paginationState?.load()
    const onUpdatePage = paginationState?.pagination.value['onUpdate:page']
    if (typeof onUpdatePage === 'function') {
      onUpdatePage(3)
    }
    await flushPromises()

    expect(fetchPage).toHaveBeenLastCalledWith({ page: 3, size: 20 })
    expect(paginationState?.page.value).toBe(3)

    const onUpdatePageSize = paginationState?.pagination.value['onUpdate:pageSize']
    if (typeof onUpdatePageSize === 'function') {
      onUpdatePageSize(50)
    }
    await flushPromises()

    expect(fetchPage).toHaveBeenLastCalledWith({ page: 1, size: 50 })
    expect(paginationState?.page.value).toBe(1)
    expect(paginationState?.pageSize.value).toBe(50)

    wrapper.unmount()
  })

  it('ignores stale responses from an older request', async () => {
    let resolveFirst: ((result: PaginationResult<TestRecord>) => void) | undefined
    let resolveSecond: ((result: PaginationResult<TestRecord>) => void) | undefined
    const fetchPage = vi
      .fn<PaginationFetcher<TestRecord>>()
      .mockImplementationOnce(
        () =>
          new Promise((resolve) => {
            resolveFirst = resolve
          }),
      )
      .mockImplementationOnce(
        () =>
          new Promise((resolve) => {
            resolveSecond = resolve
          }),
      )
    let paginationState: ReturnType<typeof usePagination<TestRecord>> | undefined
    const wrapper = mount(
      defineComponent({
        setup() {
          paginationState = usePagination(fetchPage, { immediate: false })
          return paginationState
        },
        template: '<div />',
      }),
    )

    const firstRequest = paginationState?.load()
    paginationState?.handlePageChange(2)
    resolveSecond?.(createPage(2, 20, [{ id: 2 }], 40))
    await flushPromises()
    resolveFirst?.(createPage(1, 20, [{ id: 1 }], 40))
    await firstRequest
    await flushPromises()

    expect(paginationState?.items.value).toEqual([{ id: 2 }])
    expect(paginationState?.page.value).toBe(2)
    expect(paginationState?.loading.value).toBe(false)

    wrapper.unmount()
  })

  it('corrects a page that became empty after data changes', async () => {
    const fetchPage = vi
      .fn<PaginationFetcher<TestRecord>>()
      .mockResolvedValueOnce(createPage(3, 20, [], 21))
      .mockResolvedValueOnce(createPage(2, 20, [{ id: 2 }], 21))
    let paginationState: ReturnType<typeof usePagination<TestRecord>> | undefined
    const wrapper = mount(
      defineComponent({
        setup() {
          paginationState = usePagination(fetchPage, {
            immediate: false,
            initialPage: 3,
          })
          return paginationState
        },
        template: '<div />',
      }),
    )

    await paginationState?.load()

    expect(fetchPage).toHaveBeenNthCalledWith(1, { page: 3, size: 20 })
    expect(fetchPage).toHaveBeenNthCalledWith(2, { page: 2, size: 20 })
    expect(paginationState?.items.value).toEqual([{ id: 2 }])
    expect(paginationState?.page.value).toBe(2)

    wrapper.unmount()
  })

  it('stores errors and can reset without reloading', async () => {
    const requestError = new Error('request failed')
    const fetchPage = vi.fn<PaginationFetcher<TestRecord>>().mockRejectedValue(requestError)
    let paginationState: ReturnType<typeof usePagination<TestRecord>> | undefined
    const wrapper = mount(
      defineComponent({
        setup() {
          paginationState = usePagination(fetchPage, {
            immediate: false,
            initialPage: 2,
            initialPageSize: 50,
          })
          return paginationState
        },
        template: '<div />',
      }),
    )

    await paginationState?.load()
    expect(paginationState?.error.value).toBe(requestError)
    expect(paginationState?.loading.value).toBe(false)

    await paginationState?.reset({ reload: false })
    await nextTick()
    expect(paginationState?.page.value).toBe(2)
    expect(paginationState?.pageSize.value).toBe(50)
    expect(fetchPage).toHaveBeenCalledOnce()

    wrapper.unmount()
  })

  it('invalidates a pending request when reset skips reloading', async () => {
    let resolveRequest: ((result: PaginationResult<TestRecord>) => void) | undefined
    const fetchPage = vi.fn<PaginationFetcher<TestRecord>>().mockImplementation(
      () =>
        new Promise((resolve) => {
          resolveRequest = resolve
        }),
    )
    let paginationState: ReturnType<typeof usePagination<TestRecord>> | undefined
    const wrapper = mount(
      defineComponent({
        setup() {
          paginationState = usePagination(fetchPage, { immediate: false })
          return paginationState
        },
        template: '<div />',
      }),
    )

    paginationState?.handlePageChange(2)
    await paginationState?.reset({ reload: false })
    resolveRequest?.(createPage(2, 20, [{ id: 2 }], 40))
    await flushPromises()

    expect(paginationState?.page.value).toBe(1)
    expect(paginationState?.items.value).toEqual([])
    expect(paginationState?.loading.value).toBe(false)

    wrapper.unmount()
  })
})
