import type { Ref } from 'vue'

export interface AppUpdateManifest {
  buildId: string
  builtAt?: string
}

export interface AppUpdateOptions {
  enabled?: Readonly<Ref<boolean>>
  immediate?: boolean
  interval?: number
}
