import { defineAsyncComponent } from 'vue'
import type { Component } from 'vue'
import { RouterView } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

import type { UserRoute } from '@/types'

type ViewLoader = () => Promise<{ default: Component }>

const viewLoaders = import.meta.glob('../views/**/*.vue') as Record<string, ViewLoader>

const routeComponentAliases: Record<string, string> = {
  'home/index': 'home/index',
  'system/user/index': 'backend/index',
  'system/role/index': 'backend/index',
  'system/menu/index': 'backend/index',
  'system/dept/index': 'backend/index',
  'system/post/index': 'backend/index',
  'system/dict/index': 'backend/index',
  'system/file/index': 'backend/index',
  'system/config/index': 'backend/index',
  'system/notice/index': 'backend/index',
  'monitor/log/index': 'backend/index',
  'monitor/online/index': 'backend/index',
  'monitor/job/index': 'backend/index',
}

const normalizeComponentName = (componentName: string): string =>
  componentName.replace(/^\/+|\.vue$/g, '')

export const resolveRouteComponent = (componentName: string | null): Component | null => {
  if (!componentName) {
    return null
  }

  const normalizedName = normalizeComponentName(componentName)
  if (!Object.prototype.hasOwnProperty.call(routeComponentAliases, normalizedName)) {
    return null
  }

  const aliasedName = routeComponentAliases[normalizedName]
  const viewPath = `../views/${aliasedName}.vue`
  if (!Object.prototype.hasOwnProperty.call(viewLoaders, viewPath)) {
    return null
  }

  const loader = viewLoaders[viewPath]
  return loader ? defineAsyncComponent(loader) : null
}

const normalizeRoutePath = (path: string): string => path.replace(/^\/+|\/+$/g, '')

const toRouteMeta = (route: UserRoute) => ({
  title: route.meta.title,
  menuType: route.meta.menuType,
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

  const component = resolveRouteComponent(route.component)
  const isExternalMenu = route.meta.menuType === 'L' || route.meta.menuType === 'W'
  if (!component && children.length === 0 && !isExternalMenu) {
    return null
  }

  const firstNavigableChild = children.find((child) => {
    const childMenuType = child.meta?.menuType
    return child.name !== undefined && childMenuType !== 'L' && childMenuType !== 'W'
  })
  const redirect =
    route.redirect ??
    (!component && firstNavigableChild?.name !== undefined
      ? { name: firstNavigableChild.name }
      : undefined)

  return {
    path: normalizeRoutePath(route.path),
    name: route.name,
    component: component ?? RouterView,
    redirect,
    meta: toRouteMeta(route),
    children,
  }
}

export const buildDynamicRoutes = (routes: UserRoute[]): RouteRecordRaw[] =>
  routes.map(toRouteRecord).filter((route): route is RouteRecordRaw => route !== null)

export const findFirstVisibleRouteName = (routes: UserRoute[]): string | null => {
  for (const route of routes) {
    if (route.hidden) {
      continue
    }

    if (resolveRouteComponent(route.component)) {
      return route.name
    }

    const childName = findFirstVisibleRouteName(route.children)
    if (childName) {
      return childName
    }
  }

  return null
}
