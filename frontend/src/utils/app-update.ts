import type { AppUpdateManifest } from '@/types'

export const APP_UPDATE_MANIFEST_FILE = 'version.json'
export const APP_BUILD_ID = __APP_BUILD_ID__

const toError = (value: unknown): Error =>
  value instanceof Error ? value : new Error('前端更新清单请求失败')

export const isAppUpdateManifest = (value: unknown): value is AppUpdateManifest => {
  if (typeof value !== 'object' || value === null) {
    return false
  }

  const manifest = value as Record<string, unknown>
  return (
    typeof manifest.buildId === 'string' &&
    manifest.buildId.trim().length > 0 &&
    (manifest.builtAt === undefined || typeof manifest.builtAt === 'string')
  )
}

export const getAppUpdateManifestUrl = (): string | null => {
  if (typeof window === 'undefined') {
    return null
  }

  const baseUrl = new URL(import.meta.env.BASE_URL || '/', window.location.origin)
  const manifestUrl = new URL(APP_UPDATE_MANIFEST_FILE, baseUrl)
  manifestUrl.searchParams.set('_t', Date.now().toString())
  return manifestUrl.toString()
}

export const fetchAppUpdateManifest = async (
  signal?: AbortSignal,
): Promise<AppUpdateManifest | null> => {
  const manifestUrl = getAppUpdateManifestUrl()
  if (!manifestUrl) {
    return null
  }

  const response = await globalThis.fetch(manifestUrl, {
    cache: 'no-store',
    credentials: 'same-origin',
    signal,
  })

  if (!response.ok) {
    throw new Error(`前端更新清单请求失败：${response.status}`)
  }

  const payload: unknown = await response.json()
  if (!isAppUpdateManifest(payload)) {
    throw new Error('前端更新清单格式无效')
  }

  return payload
}

export const forceReloadApp = (): void => {
  if (typeof window !== 'undefined') {
    window.location.reload()
  }
}

export { toError as toAppUpdateError }
