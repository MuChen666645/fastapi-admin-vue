import type { CurrentUserResponse, UserRoute } from '@/types'
import {
  isRecord,
  readBoolean,
  readNumber,
  readString,
  requireNumber,
  requireString,
} from '@/utils/guards/api'
import {
  isSafeExternalLink,
  isSafeRouteName,
  isSafeRoutePath,
  isUserRouteMenuType,
} from '@/utils/guards/route'

const parseUserRoute = (value: unknown): UserRoute => {
  if (!isRecord(value)) {
    throw new Error('接口路由节点无效')
  }

  const path = requireString(value.path, 'path')
  const name = requireString(value.name, 'name')
  const component = readString(value.component)
  const redirect = readString(value.redirect)

  if (!isSafeRoutePath(path) || !isSafeRouteName(name)) {
    throw new Error('接口路由路径或名称无效')
  }

  if (redirect !== null && !isSafeRoutePath(redirect)) {
    throw new Error('接口路由重定向无效')
  }

  const metaValue = isRecord(value.meta) ? value.meta : {}
  const menuTypeValue = readString(metaValue.menuType, 'C') ?? 'C'
  if (!isUserRouteMenuType(menuTypeValue)) {
    throw new Error('接口菜单类型无效')
  }

  const menuType = menuTypeValue
  const link = readString(metaValue.link)
  if (link !== null) {
    const isLinkedMenu = menuType === 'L' || menuType === 'I' || menuType === 'W'
    const isValidLink = isLinkedMenu ? isSafeExternalLink(link) : isSafeRoutePath(link)
    if (!isValidLink) {
      throw new Error('接口外链未被允许')
    }
  }

  const children = Array.isArray(value.children) ? value.children : []
  const parsedChildren = children.flatMap((child) => {
    try {
      return [parseUserRoute(child)]
    } catch {
      return []
    }
  })

  return {
    path,
    name,
    component,
    redirect,
    hidden: readBoolean(value.hidden, false),
    meta: {
      title: readString(metaValue.title, name) ?? name,
      menuType,
      icon: readString(metaValue.icon),
      noCache: readBoolean(metaValue.noCache, true),
      link,
    },
    children: parsedChildren,
  }
}

export const parseCurrentUserResponse = (value: unknown): CurrentUserResponse => {
  if (!isRecord(value) || !isRecord(value.user)) {
    throw new Error('当前用户响应无效')
  }

  if (!Array.isArray(value.permissions)) {
    throw new Error('当前用户权限响应无效')
  }

  const roles = Array.isArray(value.roles) ? value.roles : []

  return {
    posts: Array.isArray(value.posts) ? value.posts : [],
    user: {
      id: requireNumber(value.user.id, 'user.id'),
      username: requireString(value.user.username, 'user.username'),
      nickname: readString(value.user.nickname),
      email: readString(value.user.email),
      phone: readString(value.user.phone),
      avatar: readString(value.user.avatar),
      status:
        typeof value.user.status === 'number' || typeof value.user.status === 'string'
          ? value.user.status
          : '0',
    },
    roles: roles.flatMap((role) => {
      if (!isRecord(role)) {
        return []
      }

      return [
        {
          id: readNumber(role.id, 0) ?? 0,
          name: readString(role.name, '') ?? '',
          code: readString(role.code, '') ?? '',
        },
      ]
    }),
    permissions: value.permissions.flatMap((permission) => {
      const parsedPermission = readString(permission)
      return parsedPermission === null ? [] : [parsedPermission]
    }),
  }
}

export const parseUserRoutes = (value: unknown): UserRoute[] => {
  if (!Array.isArray(value)) {
    throw new Error('用户路由响应无效')
  }

  const parsedRoutes = value.flatMap((route) => {
    try {
      return [parseUserRoute(route)]
    } catch {
      return []
    }
  })
  const routeNames = new Set<string>()

  const removeDuplicateRoutes = (route: UserRoute): UserRoute | null => {
    if (routeNames.has(route.name)) {
      return null
    }

    routeNames.add(route.name)
    return {
      ...route,
      children: route.children
        .map(removeDuplicateRoutes)
        .filter((child): child is UserRoute => child !== null),
    }
  }

  return parsedRoutes
    .map(removeDuplicateRoutes)
    .filter((route): route is UserRoute => route !== null)
}
