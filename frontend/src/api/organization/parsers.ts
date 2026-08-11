import type {
  DepartmentDetail,
  DepartmentListItem,
  DepartmentOption,
  DepartmentStatus,
  PaginationResult,
  PostOption,
} from '@/types'
import { isRecord, readString, requireNumber, requireString } from '@/utils/guards/api'

const parseStatus = (value: unknown): DepartmentStatus => {
  const status = requireString(value, 'status')
  if (status !== '0' && status !== '1') {
    throw new Error('接口字段 status 无效')
  }

  return status
}

const parseInteger = (value: unknown, fieldName: string): number => {
  const number = requireNumber(value, fieldName)
  if (!Number.isInteger(number)) {
    throw new Error(`接口字段 ${fieldName} 无效`)
  }

  return number
}

const parseNullableInteger = (value: unknown, fieldName: string): number | null => {
  if (value === null || value === undefined) {
    return null
  }

  return parseInteger(value, fieldName)
}

const parseDepartmentFields = (value: unknown): DepartmentDetail => {
  if (!isRecord(value)) {
    throw new Error('部门数据无效')
  }

  return {
    dept_id: parseInteger(value.dept_id, 'dept_id'),
    parent_id: parseNullableInteger(value.parent_id, 'parent_id'),
    ancestors: requireString(value.ancestors, 'ancestors'),
    dept_name: requireString(value.dept_name, 'dept_name'),
    order_num: parseInteger(value.order_num, 'order_num'),
    leader: readString(value.leader),
    phone: readString(value.phone),
    email: readString(value.email),
    status: parseStatus(value.status),
    create_time: requireString(value.create_time, 'create_time'),
    update_time: requireString(value.update_time, 'update_time'),
  }
}

const parseDepartment = (value: unknown): DepartmentListItem => {
  if (!isRecord(value) || !Array.isArray(value.children)) {
    throw new Error('部门树数据无效')
  }

  return {
    ...parseDepartmentFields(value),
    children: value.children.map(parseDepartment),
  }
}

const toDepartmentOption = (item: DepartmentListItem): DepartmentOption => ({
  dept_id: item.dept_id,
  dept_name: item.dept_name,
  status: item.status,
  children: item.children.map(toDepartmentOption),
})

const parsePost = (value: unknown): PostOption => {
  if (!isRecord(value)) {
    throw new Error('岗位数据无效')
  }

  return {
    post_id: parseInteger(value.post_id, 'post_id'),
    post_code: requireString(value.post_code, 'post_code'),
    post_name: requireString(value.post_name, 'post_name'),
    status: parseStatus(value.status),
  }
}

const parsePageNumber = (value: unknown, fieldName: string, minimum: number): number => {
  const number = parseInteger(value, fieldName)
  if (number < minimum) {
    throw new Error(`接口字段 ${fieldName} 无效`)
  }

  return number
}

export const parseDepartmentTree = (value: unknown): DepartmentListItem[] => {
  if (!Array.isArray(value)) {
    throw new Error('部门列表响应无效')
  }

  return value.map(parseDepartment)
}

export const parseDepartmentDetail = (value: unknown): DepartmentDetail =>
  parseDepartmentFields(value)

export const parseDepartmentOptions = (value: unknown): DepartmentOption[] =>
  parseDepartmentTree(value).map(toDepartmentOption)

export const parseDepartmentList = parseDepartmentOptions

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
