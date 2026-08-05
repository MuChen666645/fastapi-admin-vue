import type { UserRoute } from './api'
import type { Component, VNode } from 'vue'
import type { RouteLocationNormalizedLoaded } from 'vue-router'

export type AuthenticatedRouteRegistrar = (serverRoutes: UserRoute[]) => void

export type ViewLoader = () => Promise<{ default: Component }>

export type RouteComponent = Component | ViewLoader

export type RouteViewComponent = Component | VNode

export type RouteCacheTarget = RouteLocationNormalizedLoaded

export interface RouteViewSlot {
  Component: VNode | null
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

export interface RouteMenuItem {
  key?: string | number
  children?: readonly RouteMenuItem[]
}

export interface RouteMenuState {
  activeKey: string | null
  expandedKeys: string[]
}
