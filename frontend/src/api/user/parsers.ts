import type {
  CurrentUserResponse,
  PaginationResult,
  UserDetail,
  UserImportError,
  UserImportResult,
  UserListItem,
  UserRoleOption,
  UserPostOption,
  UserOption,
  UserRoute,
  UserSex,
} from '@/types'
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

const parseStatus = (value: unknown): '0' | '1' => {
  const status = readString(value)
  if (status !== '0' && status !== '1') {
    throw new Error('接口字段 status 无效')
  }

  return status
}

const parseSex = (value: unknown): UserSex | null => {
  const sex = readString(value)
  if (sex === null) {
    return null
  }

  if (sex !== '0' && sex !== '1') {
    throw new Error('接口字段 sex 无效')
  }

  return sex
}

const parsePageNumber = (value: unknown, fieldName: string, minimum: number): number => {
  const number = requireNumber(value, fieldName)
  if (!Number.isInteger(number) || number < minimum) {
    throw new Error(`接口字段 ${fieldName} 无效`)
  }

  return number
}

const parseUserImportError = (value: unknown): UserImportError => {
  if (!isRecord(value)) {
    throw new Error('用户导入错误数据无效')
  }

  return {
    row: parsePageNumber(value.row, 'errors.row', 2),
    message: requireString(value.message, 'errors.message'),
  }
}

const parseUserListItem = (value: unknown): UserListItem => {
  if (!isRecord(value)) {
    throw new Error('用户数据无效')
  }

  return {
    id: parsePageNumber(value.id, 'id', 1),
    create_time: requireString(value.create_time, 'create_time'),
    username: requireString(value.username, 'username'),
    email: readString(value.email),
    phone: readString(value.phone),
    role_id: readNumber(value.role_id),
    dept_id: readNumber(value.dept_id),
    nickname: readString(value.nickname),
    sex: parseSex(value.sex),
    avatar: readString(value.avatar),
    update_time: readString(value.update_time),
    status: parseStatus(value.status),
    version: readNumber(value.version),
  }
}

const parseUserOption = (value: unknown): UserOption => {
  if (!isRecord(value)) {
    throw new Error('用户下拉数据无效')
  }

  return {
    id: requireNumber(value.id, 'id'),
    username: requireString(value.username, 'username'),
    nickname: readString(value.nickname),
  }
}

export const parseUserOptions = (value: unknown): UserOption[] => {
  if (!Array.isArray(value)) {
    throw new Error('用户下拉列表响应无效')
  }

  return value.map(parseUserOption)
}

const parseUserRole = (value: unknown): UserRoleOption => {
  if (!isRecord(value)) {
    throw new Error('用户角色数据无效')
  }

  return {
    id: parsePageNumber(value.id, 'role.id', 1),
    name: requireString(value.name, 'role.name'),
    code: requireString(value.code, 'role.code'),
    description: readString(value.description),
    status: parseStatus(value.status),
  }
}

const parseUserPost = (value: unknown): UserPostOption => {
  if (!isRecord(value)) {
    throw new Error('用户岗位数据无效')
  }

  return {
    post_id: parsePageNumber(value.post_id, 'post.post_id', 1),
    post_code: requireString(value.post_code, 'post.post_code'),
    post_name: requireString(value.post_name, 'post.post_name'),
    status: parseStatus(value.status),
  }
}

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

export const parseUserListPage = (value: unknown): PaginationResult<UserListItem> => {
  if (!isRecord(value) || !Array.isArray(value.items)) {
    throw new Error('用户分页响应无效')
  }

  return {
    items: value.items.map(parseUserListItem),
    total: parsePageNumber(value.total, 'total', 0),
    page: parsePageNumber(value.page, 'page', 1),
    size: parsePageNumber(value.size, 'size', 1),
    pages: parsePageNumber(value.pages, 'pages', 0),
  }
}

export const parseUserDetail = (value: unknown): UserDetail => {
  if (!isRecord(value) || !isRecord(value.user)) {
    throw new Error('用户详情响应无效')
  }

  return {
    user: parseUserListItem(value.user),
    roles: Array.isArray(value.roles) ? value.roles.map(parseUserRole) : [],
    posts: Array.isArray(value.posts) ? value.posts.map(parseUserPost) : [],
    permissions: Array.isArray(value.permissions)
      ? value.permissions.flatMap((permission) => {
          const parsedPermission = readString(permission)
          return parsedPermission === null ? [] : [parsedPermission]
        })
      : [],
  }
}

export const parseUserImportResult = (value: unknown): UserImportResult => {
  if (!isRecord(value) || !Array.isArray(value.errors)) {
    throw new Error('用户导入响应无效')
  }

  return {
    imported: parsePageNumber(value.imported, 'imported', 0),
    failed: parsePageNumber(value.failed, 'failed', 0),
    errors: value.errors.map(parseUserImportError),
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
