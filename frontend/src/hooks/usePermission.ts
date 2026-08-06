import { useAuthStore } from '@/stores'
import { hasPermission as matchesPermission } from '@/utils/permissions'

export const usePermission = () => {
  const auth = useAuthStore()

  const hasPermission = (permission: string): boolean =>
    matchesPermission(auth.permissions, permission)

  const hasAnyPermission = (permissions: ReadonlyArray<string>): boolean =>
    permissions.some((permission) => hasPermission(permission))

  const hasAllPermissions = (permissions: ReadonlyArray<string>): boolean =>
    permissions.every((permission) => hasPermission(permission))

  return {
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
  }
}
