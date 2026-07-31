import type { UserRouteMenuType } from './api'

export interface BreadcrumbItem {
  key: string
  name: string | symbol | null | undefined
  path: string
  title: string
  menuType: UserRouteMenuType
  link: string | null
  isCurrent: boolean
}
