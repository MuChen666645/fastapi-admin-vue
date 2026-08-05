import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

import type { AppUpdateManifest, AppUpdateOptions } from '@/types'
import {
  APP_BUILD_ID,
  fetchAppUpdateManifest,
  forceReloadApp,
  toAppUpdateError,
} from '@/utils/app-update'

const DEFAULT_INTERVAL = 5 * 60 * 1000
const MIN_INTERVAL = 10 * 1000

const normalizeInterval = (value: number | undefined): number => {
  if (typeof value !== 'number' || !Number.isFinite(value)) {
    return DEFAULT_INTERVAL
  }

  return Math.max(MIN_INTERVAL, Math.trunc(value))
}

export const useAppUpdate = (options: AppUpdateOptions = {}) => {
  const enabled = options.enabled ?? ref(true)
  const interval = normalizeInterval(options.interval)
  const currentBuildId = APP_BUILD_ID
  const hasUpdate = ref(false)
  const checking = ref(false)
  const latestManifest = ref<AppUpdateManifest | null>(null)
  const lastError = ref<Error | null>(null)

  let timer: number | null = null
  let activeController: AbortController | null = null

  const check = async (): Promise<boolean> => {
    if (checking.value) {
      return hasUpdate.value
    }

    const controller = typeof AbortController === 'undefined' ? null : new AbortController()
    activeController?.abort()
    activeController = controller
    checking.value = true
    lastError.value = null

    try {
      const manifest = await fetchAppUpdateManifest(controller?.signal)
      if (!manifest) {
        return hasUpdate.value
      }

      latestManifest.value = manifest
      hasUpdate.value = manifest.buildId !== currentBuildId
      return hasUpdate.value
    } catch (error) {
      if (!(error instanceof Error && error.name === 'AbortError')) {
        lastError.value = toAppUpdateError(error)
      }

      return hasUpdate.value
    } finally {
      if (activeController === controller) {
        activeController = null
        checking.value = false
      }
    }
  }

  const stop = (): void => {
    if (timer !== null) {
      if (typeof window === 'undefined') {
        clearInterval(timer)
      } else {
        window.clearInterval(timer)
      }
      timer = null
    }

    activeController?.abort()
    activeController = null
    checking.value = false
  }

  const start = (): void => {
    stop()
    if (typeof window === 'undefined') {
      return
    }

    if (options.immediate !== false) {
      void check()
    }

    timer = window.setInterval(() => {
      void check()
    }, interval)
  }

  const stopEnabledWatch = watch(enabled, (isEnabled) => {
    if (isEnabled) {
      start()
      return
    }

    stop()
  })

  onMounted(() => {
    if (enabled.value) {
      start()
    }
  })

  onBeforeUnmount(() => {
    stopEnabledWatch()
    stop()
  })

  return {
    currentBuildId,
    hasUpdate,
    checking,
    latestManifest,
    lastError,
    check,
    start,
    stop,
    reload: forceReloadApp,
  }
}
