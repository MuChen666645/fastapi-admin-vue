import { computed, defineComponent, h, onBeforeUnmount, type Component, type VNode } from 'vue'
import { RouterView, useRoute } from 'vue-router'

import { getRouteCacheName, isRouteCacheable } from '@/router/route-cache'
import { useTabsStore } from '@/stores'
import type { RouteCacheTarget, RouteViewComponent } from '@/types'

const getRouteKey = (targetRoute: RouteCacheTarget): string =>
  String(targetRoute.name ?? targetRoute.path)

const isComponentType = (value: VNode['type']): value is Component =>
  typeof value === 'object' || typeof value === 'function'

export const useRouteCache = () => {
  const route = useRoute()
  const tabsStore = useTabsStore()
  const routeComponentCache = new Map<string, Component>()

  const cachedComponentNames = computed(() => {
    const currentCacheName = isRouteCacheable(route) ? [getRouteCacheName(getRouteKey(route))] : []

    return [...new Set([...tabsStore.cachedComponentNames, ...currentCacheName])]
  })

  const getCachedRouteComponent = (
    component: VNode | null | undefined,
    targetRoute: RouteCacheTarget,
  ): RouteViewComponent | null | undefined => {
    if (!component || !isRouteCacheable(targetRoute)) {
      return component
    }

    const componentType = component.type
    if (!isComponentType(componentType)) {
      return component
    }

    const cacheName = getRouteCacheName(getRouteKey(targetRoute))
    const cachedComponent = routeComponentCache.get(cacheName)
    if (cachedComponent) {
      return cachedComponent
    }

    const routeSnapshot: RouteCacheTarget = {
      ...targetRoute,
      matched: [...targetRoute.matched],
      meta: { ...targetRoute.meta },
      params: { ...targetRoute.params },
      query: { ...targetRoute.query },
    }
    const componentProps = component.props ?? {}
    const routeComponent = defineComponent({
      name: cacheName,
      setup: () => () =>
        componentType === RouterView
          ? h(RouterView, { ...componentProps, route: routeSnapshot })
          : h(componentType, componentProps),
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
