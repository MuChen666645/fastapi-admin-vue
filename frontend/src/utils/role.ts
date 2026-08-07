const PROTECTED_ADMIN_ROLE_CODE = 'admin'

export const isProtectedAdminRole = (code: string): boolean =>
  code.trim().toLowerCase() === PROTECTED_ADMIN_ROLE_CODE
