import type { RoleOption } from '@/types'
import { requestJson } from '@/utils/request'

import { parseRoleOptions } from './parsers'

export const fetchRoleOptions = (): Promise<RoleOption[]> =>
  requestJson('/role/options', {}, parseRoleOptions)
