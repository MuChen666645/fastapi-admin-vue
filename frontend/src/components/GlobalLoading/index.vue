<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import { useRouter, type RouteLocationNormalized } from 'vue-router'

import carLoadingAnimation from '@/assets/lottie/car-loading3-data.json'
import { useLottie } from '@/hooks'
import { getRouteCacheName, isRouteCacheable } from '@/router/route-cache'
import { useRouteLoadingStore } from '@/stores/modules/route-loading'
import { useTabsStore } from '@/stores/modules/tabs'

defineOptions({ name: 'GlobalLoading' })

const router = useRouter()
const routeLoading = useRouteLoadingStore()
const tabsStore = useTabsStore()
const animationContainer = ref<HTMLElement | null>(null)
const { pause, play } = useLottie(animationContainer, carLoadingAnimation)
const isVisible = computed(() => routeLoading.visible && routeLoading.scope === 'screen')

watch(isVisible, (visible) => {
  if (visible) {
    play()
    return
  }

  pause()
})

const isLayoutRoute = (targetRoute: Pick<RouteLocationNormalized, 'matched'>): boolean =>
  targetRoute.matched.some((matchedRoute) => matchedRoute.name === 'app')

const isRouteAlreadyCached = (
  targetRoute: Pick<RouteLocationNormalized, 'meta' | 'name' | 'path'>,
): boolean => {
  if (!isRouteCacheable(targetRoute)) {
    return false
  }

  const routeKey = String(targetRoute.name ?? targetRoute.path)
  return tabsStore.cachedComponentNames.includes(getRouteCacheName(routeKey))
}

const removeBeforeEach = router.beforeEach((to) => {
  if (isRouteAlreadyCached(to)) {
    return
  }

  const currentIsLayoutRoute = isLayoutRoute(router.currentRoute.value)
  const targetIsLayoutRoute = isLayoutRoute(to)
  const nextScope = targetIsLayoutRoute && currentIsLayoutRoute ? 'content' : 'screen'
  routeLoading.start(nextScope)
})

const removeAfterEach = router.afterEach((to) => {
  void nextTick(() => {
    routeLoading.setScope(isLayoutRoute(to) ? 'content' : 'screen')
    routeLoading.finish()
  })
})

const removeOnError = router.onError(() => {
  routeLoading.setScope(isLayoutRoute(router.currentRoute.value) ? 'content' : 'screen')
  routeLoading.finish()
})

const waitForInitialNavigation = async (): Promise<void> => {
  routeLoading.start('screen')

  try {
    await router.isReady()
    await nextTick()
  } finally {
    const currentRoute = router.currentRoute.value
    routeLoading.setScope(isLayoutRoute(currentRoute) ? 'content' : 'screen')
    routeLoading.finish()
  }
}

void waitForInitialNavigation()

onBeforeUnmount(() => {
  routeLoading.reset()
  pause()
  removeBeforeEach()
  removeAfterEach()
  removeOnError()
})
</script>

<template>
  <div
    v-show="isVisible"
    class="global-loading"
    data-testid="global-loading"
    role="status"
    aria-label="页面加载中"
    aria-live="polite"
    :aria-hidden="!isVisible"
  >
    <div ref="animationContainer" class="global-loading__animation" aria-hidden="true" />
  </div>
</template>

<style scoped>
.global-loading {
  position: fixed;
  z-index: 2000;
  inset: 0;
  display: grid;
  place-items: center;
  background: rgb(244 246 248 / 88%);
}

.global-loading__animation {
  width: min(60vw, 360px);
  aspect-ratio: 1;
}

.app-root--dark .global-loading {
  background: rgb(23 26 43 / 90%);
}

@media (width <= 480px) {
  .global-loading__animation {
    width: min(74vw, 280px);
  }
}

@media (prefers-reduced-motion: reduce) {
  .global-loading__animation {
    opacity: 0.75;
  }
}
</style>
