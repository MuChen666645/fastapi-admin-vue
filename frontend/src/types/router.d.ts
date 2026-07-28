import 'vue-router'

declare module 'vue-router' {
  interface RouteMeta {
    title?: string
    menu?: boolean
    hideBreadcrumb?: boolean
    public?: boolean
    requiresAuth?: boolean
    allowPasswordChange?: boolean
    dynamic?: boolean
    icon?: string | null
    noCache?: boolean
    link?: string | null
    serverComponent?: string | null
  }
}

export {}
