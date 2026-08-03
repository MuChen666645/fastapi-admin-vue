import { describe, expect, it } from 'vitest'

import { translateMenuTitle, translateRouteTitle } from '../utils/i18n'

describe('frontend localization', () => {
  it('translates known menu and route titles while preserving unknown server titles', () => {
    expect(translateMenuTitle('用户管理', 'en-US')).toBe('User management')
    expect(translateMenuTitle('系统监控', 'en-US')).toBe('System monitoring')
    expect(translateRouteTitle('系统设置', 'en-US')).toBe('System settings')
    expect(translateMenuTitle('自定义业务菜单', 'en-US')).toBe('自定义业务菜单')
  })
})
