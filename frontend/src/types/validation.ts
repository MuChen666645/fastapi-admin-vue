export interface PasswordPolicy {
  minLength: number
  requireUppercase: boolean
  requireLowercase: boolean
  requireDigit: boolean
  requireSpecial: boolean
}

export type PasswordValidationCode =
  'required' | 'min-length' | 'uppercase' | 'lowercase' | 'digit' | 'special' | 'username'

export type PasswordValidationResult =
  { valid: true } | { valid: false; code: PasswordValidationCode; minLength?: number }
