import { describe, expect, it } from 'vitest'

import {
  DEFAULT_PASSWORD_POLICY,
  getPasswordValidationMessageKey,
  validateEmail,
  validatePassword,
  validatePhone,
} from '../utils'

describe('validation utilities', () => {
  it('validates mainland phone numbers and email addresses', () => {
    expect(validatePhone(' 13800138000 ')).toBe(true)
    expect(validatePhone('12800138000')).toBe(false)
    expect(validatePhone(null)).toBe(false)

    expect(validateEmail('user@example.com')).toBe(true)
    expect(validateEmail('invalid-email')).toBe(false)
    expect(validateEmail('')).toBe(false)
  })

  it('mirrors the backend password policy', () => {
    expect(DEFAULT_PASSWORD_POLICY).toEqual({
      minLength: 12,
      requireUppercase: true,
      requireLowercase: true,
      requireDigit: true,
      requireSpecial: true,
    })
    expect(validatePassword('SecureValue2026!', 'operator')).toEqual({ valid: true })
    expect(validatePassword('Aa1!')).toMatchObject({ valid: false, code: 'min-length' })
    expect(validatePassword('securevalue2026!', 'operator')).toMatchObject({
      valid: false,
      code: 'uppercase',
    })
    expect(validatePassword('SECUREVALUE2026!', 'operator')).toMatchObject({
      valid: false,
      code: 'lowercase',
    })
    expect(validatePassword('SecureValue!', 'operator')).toMatchObject({
      valid: false,
      code: 'digit',
    })
    expect(validatePassword('SecureValue2026', 'operator')).toMatchObject({
      valid: false,
      code: 'special',
    })
    expect(validatePassword('OperatorSecure2026!', 'operator')).toMatchObject({
      valid: false,
      code: 'username',
    })
  })

  it('maps password validation failures to localized message keys', () => {
    expect(getPasswordValidationMessageKey('min-length')).toBe('user.form.passwordTooShort')
    expect(getPasswordValidationMessageKey('uppercase')).toBe('user.form.passwordRequiresUppercase')
    expect(getPasswordValidationMessageKey('special')).toBe('user.form.passwordRequiresSpecial')
  })
})
