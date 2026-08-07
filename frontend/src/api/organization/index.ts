import type { DepartmentOption, PostOption } from '@/types'
import { requestJson } from '@/utils/request'

import { parseDepartmentList, parsePostOptions } from './parsers'

export const fetchDepartmentOptions = (): Promise<DepartmentOption[]> =>
  requestJson('/dept/list', {}, parseDepartmentList)

export const fetchPostOptions = (): Promise<PostOption[]> =>
  requestJson('/post/options', {}, parsePostOptions)
