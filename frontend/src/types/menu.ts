export type MenuType = 'C' | 'F' | 'L' | 'I'

export type MenuStatus = '0' | '1'

export type MenuFlag = '0' | '1'

export type MenuFormMode = 'create' | 'edit'

export interface MenuItem {
  menu_id: number
  menu_name: string
  menu_path: string | null
  parent_id: number | null
  perms: string | null
  sort: number | null
  menu_type: MenuType
  link_url: string | null
  icon: string | null
  component: string | null
  is_cache: MenuFlag | null
  is_hidden: MenuFlag | null
  create_time: string
  status: MenuStatus
  update_time: string
  remark: string | null
  children: MenuItem[]
}

export type MenuDetail = Omit<MenuItem, 'children'>

export interface MenuListFilters {
  [key: string]: unknown
  menu_name: string
  status: MenuStatus | null
}

interface MenuCreateBasePayload {
  menu_name: string
  parent_id: number
  sort: number | null
  remark: string | null
}

export interface CreateRouterMenuPayload extends MenuCreateBasePayload {
  menu_type: 'C'
  menu_path: string
  icon: string | null
  component: string | null
  is_cache: MenuFlag
  is_hidden: MenuFlag
}

export interface CreateButtonMenuPayload extends MenuCreateBasePayload {
  menu_type: 'F'
  perms: string
}

export interface CreateLinkMenuPayload extends MenuCreateBasePayload {
  menu_type: 'L'
  menu_path: string
  icon: string | null
}

export interface CreateIframeMenuPayload extends MenuCreateBasePayload {
  menu_type: 'I'
  menu_path: string
  component: string
  link_url: string | null
  icon: string | null
  is_cache: MenuFlag
  is_hidden: MenuFlag
}

export type MenuCreatePayload =
  | CreateRouterMenuPayload
  | CreateButtonMenuPayload
  | CreateLinkMenuPayload
  | CreateIframeMenuPayload

export interface MenuUpdatePayload {
  menu_name?: string
  parent_id?: number | null
  icon?: string | null
  menu_path?: string | null
  component?: string | null
  is_hidden?: MenuFlag | null
  is_cache?: MenuFlag | null
  menu_type?: MenuType
  sort?: number | null
  link_url?: string | null
  perms?: string | null
  status?: MenuStatus
  remark?: string | null
}

export type MenuFormModel = Record<string, unknown> & {
  menu_name: string
  parent_id: number
  menu_type: MenuType
  menu_path: string
  perms: string
  sort: number | null
  icon: string
  component: string
  link_url: string
  is_cache: MenuFlag
  is_hidden: MenuFlag
  status: MenuStatus
  remark: string
}
