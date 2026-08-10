import type {
  MenuCreatePayload,
  MenuDetail,
  MenuItem,
  MenuListFilters,
  MenuUpdatePayload,
} from '@/types'
import { requestJson } from '@/utils/request'

import { parseMenuDetail, parseMenuList } from './parsers'

const createMenuListParameters = (filters: MenuListFilters): Record<string, string> => {
  const parameters: Record<string, string> = {}
  const menuName = filters.menu_name.trim()
  if (menuName) {
    parameters.menu_name = menuName
  }
  if (filters.status !== null) {
    parameters.status = filters.status
  }

  return parameters
}

export const fetchMenuList = (
  filters: MenuListFilters = { menu_name: '', status: null },
): Promise<MenuItem[]> =>
  requestJson('/menu/list', { params: createMenuListParameters(filters) }, parseMenuList)

export const fetchMenuDetail = (menuId: number): Promise<MenuDetail> =>
  requestJson(`/menu/${menuId}`, {}, parseMenuDetail)

export const createMenu = (payload: MenuCreatePayload): Promise<null> =>
  requestJson('/menu/add', { method: 'POST', data: payload }, () => null)

export const updateMenu = (menuId: number, payload: MenuUpdatePayload): Promise<null> =>
  requestJson(`/menu/${menuId}`, { method: 'PUT', data: payload }, () => null)

export const deleteMenu = (menuId: number): Promise<null> =>
  requestJson(`/menu/${menuId}`, { method: 'DELETE' }, () => null)
