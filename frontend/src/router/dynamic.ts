import { RouterView } from 'vue-router'
import type { Component } from 'vue'
import type { RouteRecordRaw } from 'vue-router'

import BackendModuleView from '@/views/backend/index.vue'
import HomeView from '@/views/home/index.vue'
import type { UserRoute } from '@/types/api'

const componentRegistry: Record<string, Component> = {
  'home/index': HomeView,
  'system/user/index': BackendModuleView,
  'system/role/index': BackendModuleView,
  'system/menu/index': BackendModuleView,
  'system/dept/index': BackendModuleView,
  'system/post/index': BackendModuleView,
  'system/dict/index': BackendModuleView,
  'system/file/index': BackendModuleView,
  'system/config/index': BackendModuleView,
  'system/notice/index': BackendModuleView,
  'monitor/log/index': BackendModuleView,
  'monitor/online/index': BackendModuleView,
  'monitor/job/index': BackendModuleView,
}

const normalizeRoutePath = (path: string): string => path.replace(/^\/+|\/+$/g, '')

const toRouteMeta = (route: UserRoute) => ({
  title: route.meta.title,
  menu: route.hidden !== true,
  hideBreadcrumb: false,
  icon: route.meta.icon,
  noCache: route.meta.noCache,
  link: route.meta.link,
  serverComponent: route.component,
  dynamic: true,
})

const toRouteRecord = (route: UserRoute): RouteRecordRaw | null => {
  const children = route.children
    .map(toRouteRecord)
    .filter((child): child is RouteRecordRaw => child !== null)

  const component = route.component ? componentRegistry[route.component] : null
  if (!component && children.length === 0) {
    return null
  }

  return {
    path: normalizeRoutePath(route.path),
    name: route.name,
    component: component ?? RouterView,
    redirect: route.redirect ?? undefined,
    meta: toRouteMeta(route),
    children,
  }
}

export const buildDynamicRoutes = (routes: UserRoute[]): RouteRecordRaw[] => {
  return routes.map(toRouteRecord).filter((route): route is RouteRecordRaw => route !== null)
}

export const findFirstVisibleRouteName = (routes: UserRoute[]): string | null => {
  for (const route of routes) {
    if (route.hidden) {
      continue
    }

    if (componentRegistry[route.component ?? '']) {
      return route.name
    }

    const childName = findFirstVisibleRouteName(route.children)
    if (childName) {
      return childName
    }
  }

  return null
}
