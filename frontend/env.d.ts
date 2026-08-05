/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_APP_TITLE?: string
  readonly VITE_API_BASE_URL?: string
  readonly VITE_API_PROXY_TARGET?: string
  readonly VITE_API_PROXY_ENABLED?: string
  readonly VITE_DEV_HOST?: string
  readonly VITE_DEV_PORT?: string
  readonly VITE_PREVIEW_HOST?: string
  readonly VITE_PREVIEW_PORT?: string
  readonly VITE_DEV_OPEN?: string
  readonly VITE_BASE_PATH?: string
  readonly VITE_SOURCEMAP?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

declare const __APP_BUILD_ID__: string
