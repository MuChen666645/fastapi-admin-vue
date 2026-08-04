import { describe, expect, it } from 'vitest'
import { resolveIconComponent } from '../utils'

describe('Ionicons5 动态组件解析', () => {
  it('按后端返回的组件名称解析 Ionicons5 组件', () => {
    const homeIcon = resolveIconComponent('HomeOutline')

    expect(homeIcon).not.toBeNull()
    expect(resolveIconComponent('AnalyticsOutline')).not.toBeNull()
    expect(resolveIconComponent('PeopleOutline')).not.toBeNull()
    expect(resolveIconComponent('HomeOutline')).toBe(homeIcon)
  })

  it('不为缺失或未导出的名称创建组件', () => {
    expect(resolveIconComponent(null)).toBeNull()
    expect(resolveIconComponent('user')).toBeNull()
    expect(resolveIconComponent('unknown-icon')).toBeNull()
  })
})
