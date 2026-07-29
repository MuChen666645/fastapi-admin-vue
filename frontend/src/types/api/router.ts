export interface UserRouteMeta {
  title: string
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
