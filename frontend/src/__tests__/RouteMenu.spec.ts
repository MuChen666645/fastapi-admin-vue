import { describe, expect, it } from 'vitest'

import { resolveRouteMenuState } from '../utils/route-menu'

const menuItems = [
  {
    key: 'demo',
    children: [
      {
        key: 'features',
        children: [{ key: 'utils' }],
      },
    ],
  },
]

describe('resolveRouteMenuState', () => {
  it('selects the deepest matched route and expands its menu ancestors', () => {
    expect(resolveRouteMenuState(menuItems, ['app', 'demo', 'features', 'utils'])).toEqual({
      activeKey: 'utils',
      expandedKeys: ['demo', 'features'],
    })
  })

  it('returns the nearest menu route when the current view is not a menu item', () => {
    expect(resolveRouteMenuState(menuItems, ['app', 'demo', 'features', 'settings'])).toEqual({
      activeKey: 'features',
      expandedKeys: ['demo'],
    })
  })

  it('clears menu state when no matched route is present in the menu tree', () => {
    expect(resolveRouteMenuState(menuItems, ['app', 'login'])).toEqual({
      activeKey: null,
      expandedKeys: [],
    })
  })
})
