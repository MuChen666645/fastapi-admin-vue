import type { permissionDirective } from '@/directives'

declare module '@vue/runtime-core' {
  interface GlobalDirectives {
    vPermission: typeof permissionDirective
  }
}

export {}
