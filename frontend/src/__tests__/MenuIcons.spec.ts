import { describe, expect, it } from 'vitest'
import {
  AnalyticsOutline,
  ColorPalette,
  GridOutline,
  HomeOutline,
  PeopleOutline,
} from '@vicons/ionicons5'

import { menuIconOptions, resolveMenuIcon } from '../router/menu-icons'

describe('菜单图标关联', () => {
  it('优先按后端返回的图标标识解析 Ionicons5 组件', () => {
    expect(resolveMenuIcon('ColorPalette')).toBe(ColorPalette)
    expect(resolveMenuIcon('AnalyticsOutline')).toBe(AnalyticsOutline)
    expect(resolveMenuIcon('user')).toBe(PeopleOutline)
    expect(resolveMenuIcon('dashboard')).toBe(HomeOutline)
  })

  it('对空值和未知图标使用默认图标', () => {
    expect(resolveMenuIcon(null)).toBe(GridOutline)
    expect(resolveMenuIcon('unknown-icon')).toBe(GridOutline)
  })

  it('导出供菜单创建表单使用的图标选项', () => {
    expect(menuIconOptions.some((option) => option.value === 'ColorPalette')).toBe(true)
    expect(menuIconOptions.some((option) => option.value === 'AnalyticsOutline')).toBe(true)
    expect(menuIconOptions.some((option) => option.value === 'SettingsOutline')).toBe(true)
  })
})
