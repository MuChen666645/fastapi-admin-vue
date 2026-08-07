import type { MenuItem } from '@/types'
import { requestJson } from '@/utils/request'

import { parseMenuList } from './parsers'

export const fetchMenuList = (): Promise<MenuItem[]> => requestJson('/menu/list', {}, parseMenuList)
