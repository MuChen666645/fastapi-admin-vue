import { ref } from 'vue'
import { defineStore } from 'pinia'

import type { RouteLoadingScope } from '@/types'

const MINIMUM_VISIBLE_DURATION = 240

export const useRouteLoadingStore = defineStore('route-loading', () => {
  const visible = ref(false)
  const scope = ref<RouteLoadingScope>('screen')
  let visibleAt = 0
  let finishTimer: ReturnType<typeof setTimeout> | null = null

  const clearFinishTimer = (): void => {
    if (finishTimer === null) {
      return
    }

    clearTimeout(finishTimer)
    finishTimer = null
  }

  const hide = (): void => {
    visible.value = false
  }

  const start = (nextScope: RouteLoadingScope): void => {
    clearFinishTimer()
    visibleAt = Date.now()

    scope.value = nextScope
    visible.value = true
  }

  const setScope = (nextScope: RouteLoadingScope): void => {
    scope.value = nextScope
  }

  const finish = (): void => {
    if (!visible.value) {
      return
    }

    const remainingDuration = MINIMUM_VISIBLE_DURATION - (Date.now() - visibleAt)
    if (remainingDuration <= 0) {
      hide()
      return
    }

    clearFinishTimer()
    finishTimer = setTimeout(() => {
      finishTimer = null
      hide()
    }, remainingDuration)
  }

  const reset = (): void => {
    clearFinishTimer()
    hide()
  }

  return {
    finish,
    reset,
    scope,
    setScope,
    start,
    visible,
  }
})
