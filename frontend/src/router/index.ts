import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

import { createAuthGuard } from './guards'
import { registerAuthenticatedRoutes as registerDynamicRoutes } from './dynamic'
import { clearAuthenticatedRoutes as clearDynamicRoutes } from './dynamic'
import { errorRoutes, protectedRoutes, publicRoutes } from './modules'
import type { UserRoute } from '@/types'

const routes: RouteRecordRaw[] = [...publicRoutes, ...protectedRoutes, ...errorRoutes]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

export const registerAuthenticatedRoutes = (serverRoutes: UserRoute[]): void => {
  registerDynamicRoutes(router, serverRoutes)
}

export const clearAuthenticatedRoutes = (): void => {
  clearDynamicRoutes(router)
}

router.beforeEach(createAuthGuard(router, registerAuthenticatedRoutes))

export { buildDynamicRoutes, findFirstVisibleRouteName } from './dynamic'
export default router
