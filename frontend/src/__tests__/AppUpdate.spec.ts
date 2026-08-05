import { afterEach, describe, expect, it, vi } from 'vitest'

import { flushPromises, mount } from '@vue/test-utils'
import { createPinia } from 'pinia'

import AppUpdatePrompt from '../components/AppUpdatePrompt/index.vue'
import { usePreferencesStore } from '../stores'
import { APP_BUILD_ID, fetchAppUpdateManifest, forceReloadApp, isAppUpdateManifest } from '../utils'

const createResponse = (payload: unknown, ok = true) => ({
  ok,
  status: ok ? 200 : 503,
  json: async () => payload,
})

describe('app update infrastructure', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('validates and fetches a same-origin update manifest without browser caching', async () => {
    expect(
      isAppUpdateManifest({ buildId: 'build-next', builtAt: '2026-08-05T00:00:00.000Z' }),
    ).toBe(true)
    expect(isAppUpdateManifest({ buildId: '' })).toBe(false)
    expect(isAppUpdateManifest({ buildId: 1 })).toBe(false)

    const fetchMock = vi.fn().mockResolvedValue(createResponse({ buildId: 'build-next' }))
    vi.stubGlobal('fetch', fetchMock)

    await expect(fetchAppUpdateManifest()).resolves.toEqual({ buildId: 'build-next' })
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringMatching(/\/version\.json\?_t=\d+$/),
      expect.objectContaining({ cache: 'no-store', credentials: 'same-origin' }),
    )
  })

  it('renders the update prompt only when auto update is enabled', async () => {
    const fetchMock = vi.fn().mockResolvedValue(createResponse({ buildId: 'build-next' }))
    vi.stubGlobal('fetch', fetchMock)

    const enabledWrapper = mount(AppUpdatePrompt, {
      global: { plugins: [createPinia()] },
    })
    await flushPromises()

    expect(enabledWrapper.text()).toContain('发现新版本')
    expect(enabledWrapper.find('.app-update-prompt__content button').text()).toContain('立即刷新')
    enabledWrapper.unmount()

    const disabledPinia = createPinia()
    usePreferencesStore(disabledPinia).autoUpdate = false
    const disabledWrapper = mount(AppUpdatePrompt, {
      global: { plugins: [disabledPinia] },
    })
    await flushPromises()

    expect(disabledWrapper.text()).not.toContain('发现新版本')
    disabledWrapper.unmount()
  })

  it('forces a full browser reload when requested', () => {
    const reload = vi.fn()
    vi.stubGlobal('window', { location: { reload } })

    forceReloadApp()

    expect(reload).toHaveBeenCalledOnce()
    expect(APP_BUILD_ID).toEqual(expect.any(String))
  })
})
