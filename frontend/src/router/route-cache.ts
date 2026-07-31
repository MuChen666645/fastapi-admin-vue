import type { RouteLocationNormalizedLoaded } from 'vue-router'

export const getRouteCacheName = (routeKey: string): string => `RouteTab_${routeKey}`

export const isRouteCacheable = (
  targetRoute: Pick<RouteLocationNormalizedLoaded, 'meta'>,
): boolean => targetRoute.meta.noCache === false
