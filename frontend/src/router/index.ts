import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

import { createAuthGuard } from './guards'
import { errorRoutes, protectedRoutes, publicRoutes } from './modules'
import { buildDynamicRoutes } from './route-utils'
import type { UserRoute } from '@/types'

const routes: RouteRecordRaw[] = [...publicRoutes, ...protectedRoutes, ...errorRoutes]

let registeredRouteNames: string[] = []

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

export const registerAuthenticatedRoutes = (serverRoutes: UserRoute[]): void => {
  if (registeredRouteNames.length > 0) {
    return
  }

  const dynamicRoutes = buildDynamicRoutes(serverRoutes)
  registeredRouteNames = dynamicRoutes.flatMap((route) => {
    if (typeof route.name !== 'string' || router.hasRoute(route.name)) {
      return []
    }

    router.addRoute('app', route)
    return [route.name]
  })
}

export const clearAuthenticatedRoutes = (): void => {
  registeredRouteNames.forEach((name) => {
    if (router.hasRoute(name)) {
      router.removeRoute(name)
    }
  })
  registeredRouteNames = []
}

router.beforeEach(createAuthGuard(router, registerAuthenticatedRoutes))

export { buildDynamicRoutes, findFirstVisibleRouteName, resolveRouteComponent } from './route-utils'
export { loadApplicationRoutes } from './route-source'
export default router
