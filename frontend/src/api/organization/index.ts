import type {
  DepartmentCreatePayload,
  DepartmentDetail,
  DepartmentListFilters,
  DepartmentListItem,
  DepartmentOption,
  DepartmentUpdatePayload,
  PaginationResult,
  PostCreatePayload,
  PostDetail,
  PostListFilters,
  PostListItem,
  PostListQuery,
  PostOption,
  PostUpdatePayload,
} from '@/types'
import { requestJson } from '@/utils/request'

import {
  parseDepartmentDetail,
  parseDepartmentOptions,
  parseDepartmentTree,
  parsePostDetail,
  parsePostOptions,
  parsePostPage,
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

const createPostListParameters = (
  params: PostListQuery,
  filters: PostListFilters,
): Record<string, string | number> => {
  const parameters: Record<string, string | number> = { page: params.page, size: params.size }
  const name = filters.name.trim()
  if (name) {
    parameters.name = name
  }
  if (filters.status !== null) {
    parameters.status = filters.status
  }

  return parameters
}

export const fetchPostList = (
  params: PostListQuery,
  filters: PostListFilters,
): Promise<PaginationResult<PostListItem>> =>
  requestJson('/post/list', { params: createPostListParameters(params, filters) }, parsePostPage)

export const fetchPostDetail = (postId: number): Promise<PostDetail> =>
  requestJson(`/post/${postId}`, {}, parsePostDetail)

export const createPost = (payload: PostCreatePayload): Promise<null> =>
  requestJson('/post/add', { method: 'POST', data: payload }, () => null)

export const updatePost = (postId: number, payload: PostUpdatePayload): Promise<null> =>
  requestJson(`/post/${postId}`, { method: 'PUT', data: payload }, () => null)

export const deletePost = (postId: number): Promise<null> =>
  requestJson(`/post/${postId}`, { method: 'DELETE' }, () => null)
