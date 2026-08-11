import type {
  DepartmentCreatePayload,
  DepartmentDetail,
  DepartmentListFilters,
  DepartmentListItem,
  DepartmentOption,
  DepartmentUpdatePayload,
  PostOption,
} from '@/types'
import { requestJson } from '@/utils/request'

import {
  parseDepartmentDetail,
  parseDepartmentOptions,
  parseDepartmentTree,
  parsePostOptions,
} from './parsers'

const createDepartmentListParameters = (filters: DepartmentListFilters): Record<string, string> => {
  const parameters: Record<string, string> = {}
  const name = filters.name.trim()
  if (name) {
    parameters.name = name
  }
  if (filters.status !== null) {
    parameters.status = filters.status
  }

  return parameters
}

export const fetchDepartmentList = (
  filters: DepartmentListFilters = { name: '', status: null },
): Promise<DepartmentListItem[]> =>
  requestJson(
    '/dept/list',
    { params: createDepartmentListParameters(filters) },
    parseDepartmentTree,
  )

export const fetchDepartmentOptions = (): Promise<DepartmentOption[]> =>
  requestJson('/dept/list', {}, parseDepartmentOptions)

export const fetchDepartmentDetail = (departmentId: number): Promise<DepartmentDetail> =>
  requestJson(`/dept/${departmentId}`, {}, parseDepartmentDetail)

export const createDepartment = (payload: DepartmentCreatePayload): Promise<null> =>
  requestJson('/dept/add', { method: 'POST', data: payload }, () => null)

export const updateDepartment = (
  departmentId: number,
  payload: DepartmentUpdatePayload,
): Promise<null> =>
  requestJson(`/dept/${departmentId}`, { method: 'PUT', data: payload }, () => null)

export const deleteDepartment = (departmentId: number): Promise<null> =>
  requestJson(`/dept/${departmentId}`, { method: 'DELETE' }, () => null)

export const fetchPostOptions = (): Promise<PostOption[]> =>
  requestJson('/post/options', {}, parsePostOptions)
