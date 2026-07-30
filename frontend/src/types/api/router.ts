export type UserRouteMenuType = 'C' | 'L' | 'I' | 'W'

export interface UserRouteMeta {
  title: string
  menuType: UserRouteMenuType
  icon: string | null
  noCache: boolean
  link: string | null
}

export interface UserRoute {
  path: string
  name: string
  component: string | null
  redirect: string | null
  hidden: boolean
  meta: UserRouteMeta
  children: UserRoute[]
}
