export interface ApiResponse<T> {
  code: number
  error_code?: string | null
  message: string
  data: T | null
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number | null
  must_change_password: boolean
}

export interface CaptchaImageResponse {
  captcha_id: string
  image: string
}

export interface LoginCredentials {
  loginType: 'username' | 'phone'
  identifier: string
  password: string
  captcha_id: string
  captcha: string
  mfa_code?: string
}

export interface CurrentUserResponse {
  posts: unknown[]
  user: {
    id: number
    username: string
    nickname: string | null
    email: string | null
    phone: string | null
    avatar: string | null
    status: string | number
  }
  roles: Array<{
    id: number
    name: string
    code: string
  }>
  permissions: string[]
}

export interface UserRouteMeta {
  title: string
  icon: string | null
  noCache: boolean
  link: string | null
}

export interface UserRoute {
  path: string
  name: string
  component: string | null
  redirect: string | null
  hidden: boolean
  meta: UserRouteMeta
  children: UserRoute[]
}

export const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === 'object' && value !== null

const requireString = (value: unknown, fieldName: string): string => {
  if (typeof value !== 'string' || value.trim().length === 0) {
    throw new Error(`接口字段 ${fieldName} 无效`)
  }

  return value
}

const requireNumber = (value: unknown, fieldName: string): number => {
  if (typeof value !== 'number' || !Number.isFinite(value)) {
    throw new Error(`接口字段 ${fieldName} 无效`)
  }

  return value
}

const requireBoolean = (value: unknown, fieldName: string): boolean => {
  if (typeof value !== 'boolean') {
    throw new Error(`接口字段 ${fieldName} 无效`)
  }

  return value
}

const readString = (value: unknown, fallback: string | null = null): string | null =>
  typeof value === 'string' && value.trim().length > 0 ? value : fallback

const readBoolean = (value: unknown, fallback: boolean): boolean =>
  typeof value === 'boolean' ? value : fallback

const readNumber = (value: unknown, fallback: number | null = null): number | null =>
  typeof value === 'number' && Number.isFinite(value) ? value : fallback

const isSafeRoutePath = (value: string): boolean => {
  return (
    value.length > 0 &&
    value.length <= 200 &&
    !value.includes('..') &&
    !value.includes('\\') &&
    !value.includes('//') &&
    !/[?#\s]/u.test(value) &&
    /^[A-Za-z0-9_./:-]+$/u.test(value)
  )
}

const isSafeRouteName = (value: string): boolean => {
  return value.length <= 64 && /^[\p{L}\p{N}][\p{L}\p{N}_-]*$/u.test(value)
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
  const link = readString(metaValue.link)
  if (link !== null && !isSafeRoutePath(link)) {
    throw new Error('接口外链未被允许')
  }

  const children = value.children
  const parsedChildren = (Array.isArray(children) ? children : []).flatMap((child) => {
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
      icon: readString(metaValue.icon),
      noCache: readBoolean(metaValue.noCache, true),
      link,
    },
    children: parsedChildren,
  }
}

export const parseApiResponse = (value: unknown): ApiResponse<unknown> => {
  if (!isRecord(value) || typeof value.code !== 'number' || typeof value.message !== 'string') {
    throw new Error('接口响应格式无效')
  }

  return {
    code: value.code,
    error_code: typeof value.error_code === 'string' ? value.error_code : null,
    message: value.message,
    data: value.data ?? null,
  }
}

export const parseTokenResponse = (value: unknown): TokenResponse => {
  if (!isRecord(value)) {
    throw new Error('令牌响应无效')
  }

  const accessToken = requireString(value.access_token, 'access_token')
  const refreshToken = requireString(value.refresh_token, 'refresh_token')

  return {
    access_token: accessToken,
    refresh_token: refreshToken,
    token_type: readString(value.token_type, 'bearer') ?? 'bearer',
    expires_in: readNumber(value.expires_in),
    must_change_password: requireBoolean(value.must_change_password, 'must_change_password'),
  }
}

export const parseCaptchaImageResponse = (value: unknown): CaptchaImageResponse => {
  if (!isRecord(value)) {
    throw new Error('验证码响应无效')
  }

  return {
    captcha_id: requireString(value.captcha_id, 'captcha_id'),
    image: requireString(value.image, 'image'),
  }
}

export const parseCurrentUserResponse = (value: unknown): CurrentUserResponse => {
  if (!isRecord(value) || !isRecord(value.user)) {
    throw new Error('当前用户响应无效')
  }

  const roles = value.roles
  const permissions = value.permissions
  if (!Array.isArray(permissions)) {
    throw new Error('当前用户权限响应无效')
  }

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
    roles: (Array.isArray(roles) ? roles : []).flatMap((role) => {
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
    permissions: permissions.flatMap((permission) => {
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
