import type {
  PasswordPolicy,
  PasswordValidationCode,
  PasswordValidationResult,
  TranslationKey,
} from '@/types'

export const DEFAULT_PASSWORD_POLICY: PasswordPolicy = {
  minLength: 12,
  requireUppercase: true,
  requireLowercase: true,
  requireDigit: true,
  requireSpecial: true,
}

const PHONE_PATTERN = /^1[3-9]\d{9}$/
const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
const ASCII_PUNCTUATION = new Set('!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~')

const invalidPasswordMessageKeys: Record<PasswordValidationCode, TranslationKey> = {
  required: 'user.form.passwordPlaceholder',
  'min-length': 'user.form.passwordTooShort',
  uppercase: 'user.form.passwordRequiresUppercase',
  lowercase: 'user.form.passwordRequiresLowercase',
  digit: 'user.form.passwordRequiresDigit',
  special: 'user.form.passwordRequiresSpecial',
  username: 'user.form.passwordCannotContainUsername',
}

export const validatePhone = (value: unknown): boolean =>
  typeof value === 'string' && PHONE_PATTERN.test(value.trim())

export const validateEmail = (value: unknown): boolean =>
  typeof value === 'string' && EMAIL_PATTERN.test(value.trim())

export const validatePassword = (
  value: unknown,
  username?: unknown,
  policy: PasswordPolicy = DEFAULT_PASSWORD_POLICY,
): PasswordValidationResult => {
  if (typeof value !== 'string' || value.trim().length === 0) {
    return { valid: false, code: 'required' }
  }

  if (value.length < policy.minLength) {
    return { valid: false, code: 'min-length', minLength: policy.minLength }
  }

  if (policy.requireUppercase && !/\p{Lu}/u.test(value)) {
    return { valid: false, code: 'uppercase' }
  }

  if (policy.requireLowercase && !/\p{Ll}/u.test(value)) {
    return { valid: false, code: 'lowercase' }
  }

  if (policy.requireDigit && !/\p{Nd}/u.test(value)) {
    return { valid: false, code: 'digit' }
  }

  if (
    policy.requireSpecial &&
    !Array.from(value).some((character) => ASCII_PUNCTUATION.has(character))
  ) {
    return { valid: false, code: 'special' }
  }

  if (
    typeof username === 'string' &&
    username.length > 0 &&
    value.toLocaleLowerCase().includes(username.toLocaleLowerCase())
  ) {
    return { valid: false, code: 'username' }
  }

  return { valid: true }
}

export const getPasswordValidationMessageKey = (code: PasswordValidationCode): TranslationKey =>
  invalidPasswordMessageKeys[code]
