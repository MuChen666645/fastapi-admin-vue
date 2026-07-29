import type { UserRoute } from './api'

export type AuthenticatedRouteRegistrar = (serverRoutes: UserRoute[]) => void
