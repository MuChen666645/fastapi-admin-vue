export type MenuType = 'C' | 'F' | 'L' | 'I'

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
  is_cache: '0' | '1' | null
  is_hidden: '0' | '1' | null
  create_time: string
  status: '0' | '1'
  update_time: string
  remark: string | null
  children: MenuItem[]
}
