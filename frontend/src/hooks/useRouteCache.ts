import { computed, defineComponent, h, onBeforeUnmount, type Component } from 'vue'
import type { RouteLocationNormalizedLoaded } from 'vue-router'
import { useRoute } from 'vue-router'

import { getRouteCacheName } from '@/router/route-cache'
import { useTabsStore } from '@/stores'

interface RouteCacheTarget {
  name: string | symbol | null | undefined
  path: string
  meta: RouteLocationNormalizedLoaded['meta']
}

const getRouteKey = (targetRoute: RouteCacheTarget): string =>
  String(targetRoute.name ?? targetRoute.path)

const isCacheableRoute = (targetRoute: RouteCacheTarget): boolean =>
  targetRoute.meta.noCache === false

export const useRouteCache = () => {
  const route = useRoute()
  const tabsStore = useTabsStore()
  const routeComponentCache = new Map<string, Component>()

  const cachedComponentNames = computed(() => {
    const currentCacheName = isCacheableRoute(route) ? [getRouteCacheName(getRouteKey(route))] : []

    return [...new Set([...tabsStore.cachedComponentNames, ...currentCacheName])]
  })

  const getCachedRouteComponent = (
    component: Component | null | undefined,
    targetRoute: RouteCacheTarget,
  ): Component | null | undefined => {
    if (!component || !isCacheableRoute(targetRoute)) {
      return component
    }

    const cacheName = getRouteCacheName(getRouteKey(targetRoute))
    const cachedComponent = routeComponentCache.get(cacheName)
    if (cachedComponent) {
      return cachedComponent
    }

    const routeComponent = defineComponent({
      name: cacheName,
      setup: () => () => h(component),
    })
    routeComponentCache.set(cacheName, routeComponent)
    return routeComponent
  }

  onBeforeUnmount(() => {
    routeComponentCache.clear()
  })

  return {
    cachedComponentNames,
    getCachedRouteComponent,
    getRouteKey,
  }
}
