import type { MenuItem, MenuType } from '@/types'
import { isRecord, readString, requireNumber, requireString } from '@/utils/guards/api'

const parseStatus = (value: unknown): '0' | '1' => {
  const status = requireString(value, 'status')
  if (status !== '0' && status !== '1') {
    throw new Error('接口字段 status 无效')
  }

  return status
}

const parseFlag = (value: unknown, fieldName: string): '0' | '1' | null => {
  if (value === null || value === undefined) {
    return null
  }

  const flag = requireString(value, fieldName)
  if (flag !== '0' && flag !== '1') {
    throw new Error(`接口字段 ${fieldName} 无效`)
  }

  return flag
}

const parseMenuType = (value: unknown): MenuType => {
  const menuType = requireString(value, 'menu_type') as MenuType
  if (!['C', 'F', 'L', 'I'].includes(menuType)) {
    throw new Error('接口字段 menu_type 无效')
  }

  return menuType
}

const parseNullableNumber = (value: unknown, fieldName: string): number | null => {
  if (value === null || value === undefined) {
    return null
  }

  return requireNumber(value, fieldName)
}

const parseMenu = (value: unknown): MenuItem => {
  if (!isRecord(value)) {
    throw new Error('菜单数据无效')
  }

  const children = Array.isArray(value.children) ? value.children.map(parseMenu) : []
  return {
    menu_id: requireNumber(value.menu_id, 'menu_id'),
    menu_name: requireString(value.menu_name, 'menu_name'),
    menu_path: readString(value.menu_path),
    parent_id: parseNullableNumber(value.parent_id, 'parent_id'),
    perms: readString(value.perms),
    sort: parseNullableNumber(value.sort, 'sort'),
    menu_type: parseMenuType(value.menu_type),
    link_url: readString(value.link_url),
    icon: readString(value.icon),
    component: readString(value.component),
    is_cache: parseFlag(value.is_cache, 'is_cache'),
    is_hidden: parseFlag(value.is_hidden, 'is_hidden'),
    create_time: requireString(value.create_time, 'create_time'),
    status: parseStatus(value.status),
    update_time: requireString(value.update_time, 'update_time'),
    remark: readString(value.remark),
    children,
  }
}

export const parseMenuList = (value: unknown): MenuItem[] => {
  if (!Array.isArray(value)) {
    throw new Error('菜单列表响应无效')
  }

  return value.map(parseMenu)
}
