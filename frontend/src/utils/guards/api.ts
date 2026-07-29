import type { ApiResponse } from '@/types'

export const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === 'object' && value !== null

export const requireString = (value: unknown, fieldName: string): string => {
  if (typeof value !== 'string' || value.trim().length === 0) {
    throw new Error(`接口字段 ${fieldName} 无效`)
  }

  return value
}

export const requireNumber = (value: unknown, fieldName: string): number => {
  if (typeof value !== 'number' || !Number.isFinite(value)) {
    throw new Error(`接口字段 ${fieldName} 无效`)
  }

  return value
}

export const requireBoolean = (value: unknown, fieldName: string): boolean => {
  if (typeof value !== 'boolean') {
    throw new Error(`接口字段 ${fieldName} 无效`)
  }

  return value
}

export const readString = (value: unknown, fallback: string | null = null): string | null =>
  typeof value === 'string' && value.trim().length > 0 ? value : fallback

export const readBoolean = (value: unknown, fallback: boolean): boolean =>
  typeof value === 'boolean' ? value : fallback

export const readNumber = (value: unknown, fallback: number | null = null): number | null =>
  typeof value === 'number' && Number.isFinite(value) ? value : fallback

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
