import type { DepartmentOption, PaginationResult, PostOption } from '@/types'
import { isRecord, readString, requireNumber, requireString } from '@/utils/guards/api'

const parseStatus = (value: unknown): '0' | '1' => {
  const status = readString(value, '1') ?? '1'
  if (status !== '0' && status !== '1') {
    throw new Error('接口字段 status 无效')
  }

  return status
}

const parseDepartment = (value: unknown): DepartmentOption => {
  if (!isRecord(value)) {
    throw new Error('部门数据无效')
  }

  const children = Array.isArray(value.children)
    ? value.children.flatMap((child) => {
        try {
          return [parseDepartment(child)]
        } catch {
          return []
        }
      })
    : []

  return {
    dept_id: requireNumber(value.dept_id, 'dept_id'),
    dept_name: requireString(value.dept_name, 'dept_name'),
    status: parseStatus(value.status),
    children,
  }
}

const parsePost = (value: unknown): PostOption => {
  if (!isRecord(value)) {
    throw new Error('岗位数据无效')
  }

  return {
    post_id: requireNumber(value.post_id, 'post_id'),
    post_code: requireString(value.post_code, 'post_code'),
    post_name: requireString(value.post_name, 'post_name'),
    status: parseStatus(value.status),
  }
}

const parsePageNumber = (value: unknown, fieldName: string, minimum: number): number => {
  const number = requireNumber(value, fieldName)
  if (!Number.isInteger(number) || number < minimum) {
    throw new Error(`接口字段 ${fieldName} 无效`)
  }

  return number
}

export const parseDepartmentList = (value: unknown): DepartmentOption[] => {
  if (!Array.isArray(value)) {
    throw new Error('部门列表响应无效')
  }

  return value.map(parseDepartment)
}

export const parsePostOptions = (value: unknown): PostOption[] => {
  if (!Array.isArray(value)) {
    throw new Error('岗位下拉列表响应无效')
  }

  return value.map(parsePost)
}

export const parsePostPage = (value: unknown): PaginationResult<PostOption> => {
  if (!isRecord(value) || !Array.isArray(value.items)) {
    throw new Error('岗位分页响应无效')
  }

  return {
    items: value.items.map(parsePost),
    total: parsePageNumber(value.total, 'total', 0),
    page: parsePageNumber(value.page, 'page', 1),
    size: parsePageNumber(value.size, 'size', 1),
    pages: parsePageNumber(value.pages, 'pages', 0),
  }
}
