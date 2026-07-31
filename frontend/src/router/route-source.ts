import { fetchUserRoutes } from '@/api'
import type { UserRoute } from '@/types'

export const loadApplicationRoutes = async (): Promise<UserRoute[]> => {
  return fetchUserRoutes()
}
