import type { RouteMenuItem, RouteMenuState } from '@/types'

const findMenuPath = (
  items: readonly RouteMenuItem[],
  targetKey: string,
  ancestors: readonly string[] = [],
): string[] | null => {
  for (const item of items) {
    if (item.key === undefined) {
      continue
    }

    const key = String(item.key)
    const currentPath = [...ancestors, key]

    if (key === targetKey) {
      return currentPath
    }

    const childPath = findMenuPath(item.children ?? [], targetKey, currentPath)
    if (childPath) {
      return childPath
    }
  }

  return null
}

export const resolveRouteMenuState = (
  menuItems: readonly RouteMenuItem[],
  matchedRouteNames: readonly unknown[],
): RouteMenuState => {
  const routeNames = matchedRouteNames
    .filter((name): name is string => typeof name === 'string' && name.length > 0)
    .reverse()

  for (const routeName of routeNames) {
    const menuPath = findMenuPath(menuItems, routeName)
    if (menuPath) {
      return {
        activeKey: routeName,
        expandedKeys: menuPath.slice(0, -1),
      }
    }
  }

  return {
    activeKey: null,
    expandedKeys: [],
  }
}
