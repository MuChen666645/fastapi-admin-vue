import { defineAsyncComponent } from 'vue'
import type { Component } from 'vue'
import { RouterView } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

import type { UserRoute } from '@/types'

type ViewLoader = () => Promise<{ default: Component }>

const viewLoaders = import.meta.glob('../views/**/*.vue') as Record<string, ViewLoader>

const normalizeComponentName = (componentName: string): string =>
  componentName
    .trim()
    .replace(/\.vue$/g, '')
    .replace(/^@\/views\//, '')
    .replace(/^(?:\.\.\/|\.\/)views\//, '')
    .replace(/^\/?views\//, '')
    .replace(/^\.?\/+/, '')

const resolvedComponents = new Map<string, Component>()
const warnedComponents = new Set<string>()

const getViewLoader = (componentName: string): ViewLoader | null => {
  const viewPath = `../views/${componentName}.vue`
  return Object.prototype.hasOwnProperty.call(viewLoaders, viewPath)
    ? (viewLoaders[viewPath] ?? null)
    : null
}

const warnMissingComponent = (componentName: string, normalizedName: string): void => {
  const warningKey = normalizedName || componentName
  if (warnedComponents.has(warningKey)) {
    return
  }

  warnedComponents.add(warningKey)
  console.warn(
    `[router] 未找到路由组件：${componentName}，期望路径为 src/views/${normalizedName}.vue`,
  )
}

export const resolveRouteComponent = (componentName: string | null): Component | null => {
  if (!componentName?.trim()) {
    return null
  }

  const normalizedName = normalizeComponentName(componentName)
  if (
    !normalizedName ||
    normalizedName.includes('..') ||
    normalizedName.includes('\\') ||
    normalizedName.includes('//') ||
    !/^[A-Za-z0-9_./-]+$/u.test(normalizedName)
  ) {
    warnMissingComponent(componentName, normalizedName)
    return null
  }

  const cachedComponent = resolvedComponents.get(normalizedName)
  if (cachedComponent) {
    return cachedComponent
  }

  const loader = getViewLoader(normalizedName)
  if (!loader) {
    warnMissingComponent(componentName, normalizedName)
    return null
  }

  const component = defineAsyncComponent(loader)
  resolvedComponents.set(normalizedName, component)
  return component
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
