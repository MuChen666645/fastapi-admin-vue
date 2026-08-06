const SUPER_PERMISSION = '*:*:*'

export const hasPermission = (permissions: ReadonlyArray<string>, permission: string): boolean =>
  permissions.includes(SUPER_PERMISSION) || permissions.includes(permission)
