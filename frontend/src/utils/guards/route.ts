import type { UserRouteMenuType } from '@/types'

export const isSafeRoutePath = (value: string): boolean =>
  value.length > 0 &&
  value.length <= 200 &&
  !value.includes('..') &&
  !value.includes('\\') &&
  !value.includes('//') &&
  !/[?#\s]/u.test(value) &&
  /^[A-Za-z0-9_./:-]+$/u.test(value)

export const isSafeRouteName = (value: string): boolean =>
  value.length <= 64 && /^[\p{L}\p{N}][\p{L}\p{N}_-]*$/u.test(value)

export const isUserRouteMenuType = (value: string): value is UserRouteMenuType =>
  value === 'C' || value === 'L' || value === 'I' || value === 'W'

export const isSafeExternalLink = (value: string): boolean => {
  try {
    const url = new URL(value)
    return (url.protocol === 'http:' || url.protocol === 'https:') && !url.username && !url.password
  } catch {
    return false
  }
}
