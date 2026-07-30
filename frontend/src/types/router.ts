import type { UserRoute } from './api'

export type AuthenticatedRouteRegistrar = (serverRoutes: UserRoute[]) => void

export interface AppTab {
  key: string
  title: string
  fullPath: string
  icon: string | null
  cacheName: string | null
  cacheable: boolean
  closable: boolean
}
