const PROTECTED_ADMIN_USERNAME = 'admin'

export const isProtectedAdminUser = (username: string): boolean =>
  username.trim().toLowerCase() === PROTECTED_ADMIN_USERNAME
