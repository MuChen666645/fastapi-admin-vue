import type { NavigationGuard, Router } from 'vue-router'

import { useAuthStore } from '@/stores'
import type { AuthenticatedRouteRegistrar } from '@/types'
import { findFirstVisibleRouteName } from '../dynamic'

export const createAuthGuard =
  (router: Router, registerRoutes: AuthenticatedRouteRegistrar): NavigationGuard =>
  async (to) => {
    const auth = useAuthStore()

    if (to.name === 'login') {
      if (!auth.hasSession && auth.status === 'signed-out') {
        return true
      }

      const initialized = await auth.initializeSession()
      if (!initialized) {
        return true
      }

      if (auth.status === 'password-change-required') {
        return { name: 'change-password' }
      }

      registerRoutes(auth.routes)
      return { path: '/' }
    }

    if (to.name === 'not-found') {
      const initialized = await auth.initializeSession()
      if (!initialized || !auth.accessToken) {
        return true
      }

      if (auth.status === 'password-change-required') {
        return { name: 'change-password' }
      }

      registerRoutes(auth.routes)
      const resolvedRoute = router.resolve(to.fullPath)
      if (resolvedRoute.name && resolvedRoute.name !== 'not-found') {
        return {
          path: to.path,
          query: to.query,
          hash: to.hash,
          replace: true,
        }
      }

      return true
    }

    if (to.meta.public === true) {
      return true
    }

    const initialized = await auth.initializeSession()
    if (!initialized || !auth.accessToken) {
      return {
        name: 'login',
        query: { redirect: to.fullPath },
      }
    }

    if (auth.status === 'password-change-required' && to.name !== 'change-password') {
      return { name: 'change-password' }
    }

    if (to.name === 'app') {
      registerRoutes(auth.routes)
      const firstRouteName = findFirstVisibleRouteName(auth.routes)
      return firstRouteName ? { name: firstRouteName } : { name: 'forbidden' }
    }

    registerRoutes(auth.routes)
    return true
  }
