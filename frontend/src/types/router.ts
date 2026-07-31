import type { UserRoute } from './api'
import type { Component } from 'vue'
import type { RouteLocationNormalizedLoaded } from 'vue-router'

export type AuthenticatedRouteRegistrar = (serverRoutes: UserRoute[]) => void

export type ViewLoader = () => Promise<{ default: Component }>

export interface RouteCacheTarget {
  name: string | symbol | null | undefined
  path: string
  meta: RouteLocationNormalizedLoaded['meta']
}

export interface RouteViewSlot {
  Component: Component | null
  route: RouteLocationNormalizedLoaded
}

export interface AppTab {
  key: string
  title: string
  fullPath: string
  icon: string | null
  cacheName: string | null
  cacheable: boolean
  closable: boolean
}
