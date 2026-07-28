import BasicLayout from '@/layouts/BasicLayout/index.vue'
import ChangePasswordView from '@/views/change-password/index.vue'
import ForbiddenView from '@/views/error/403.vue'
import NotFoundView from '@/views/error/404.vue'
import LoginView from '@/views/login/index.vue'
import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

import { useAuthStore } from '@/stores/auth'
import { buildDynamicRoutes, findFirstVisibleRouteName } from './dynamic'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: {
      title: '登录',
      menu: false,
      hideBreadcrumb: true,
      public: true,
    },
  },
  {
    path: '/change-password',
    name: 'change-password',
    component: ChangePasswordView,
    meta: {
      title: '修改密码',
      menu: false,
      hideBreadcrumb: true,
      requiresAuth: true,
      allowPasswordChange: true,
    },
  },
  {
    path: '/403',
    name: 'forbidden',
    component: ForbiddenView,
    meta: {
      title: '无权限访问',
      menu: false,
      hideBreadcrumb: true,
      public: true,
    },
  },
  {
    path: '/',
    name: 'app',
    component: BasicLayout,
    meta: {
      title: '管理后台',
      menu: false,
      hideBreadcrumb: true,
      requiresAuth: true,
    },
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: NotFoundView,
    meta: {
      title: '页面不存在',
      menu: false,
      hideBreadcrumb: true,
      public: true,
    },
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

let registeredRouteNames: string[] = []

export const registerAuthenticatedRoutes = (
  serverRoutes: Parameters<typeof buildDynamicRoutes>[0],
) => {
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

router.beforeEach(async (to) => {
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

    registerAuthenticatedRoutes(auth.routes)
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

    registerAuthenticatedRoutes(auth.routes)
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
    registerAuthenticatedRoutes(auth.routes)
    const firstRouteName = findFirstVisibleRouteName(auth.routes)
    return firstRouteName ? { name: firstRouteName } : { name: 'forbidden' }
  }

  registerAuthenticatedRoutes(auth.routes)
  return true
})

export default router
