import type { AccentColorKey, RadiusScale, TranslationKey } from '@/types'

export interface AccentColorOption {
  key: AccentColorKey
  light: string
  dark: string
  hover: string
  nameKey: Extract<TranslationKey, `settings.appearance.accent.${string}`>
}

export const accentColorOptions: ReadonlyArray<AccentColorOption> = [
  {
    key: 'blue',
    light: '#6c7ce5',
    dark: '#aeb8f3',
    hover: '#5762e0',
    nameKey: 'settings.appearance.accent.blue',
  },
  {
    key: 'violet',
    light: '#7367f0',
    dark: '#b0a8ff',
    hover: '#5d51d8',
    nameKey: 'settings.appearance.accent.violet',
  },
  {
    key: 'rose',
    light: '#e94b78',
    dark: '#ff9db8',
    hover: '#d53b68',
    nameKey: 'settings.appearance.accent.rose',
  },
  {
    key: 'amber',
    light: '#d89621',
    dark: '#f5c76b',
    hover: '#b97814',
    nameKey: 'settings.appearance.accent.amber',
  },
  {
    key: 'green',
    light: '#18a058',
    dark: '#63d89b',
    hover: '#0d8747',
    nameKey: 'settings.appearance.accent.green',
  },
  {
    key: 'slate',
    light: '#34445d',
    dark: '#a8b7cf',
    hover: '#25334a',
    nameKey: 'settings.appearance.accent.slate',
  },
]

export const radiusOptions: ReadonlyArray<{
  value: RadiusScale
  labelKey: Extract<TranslationKey, `settings.appearance.radius.${string}`>
}> = [
  { value: 0, labelKey: 'settings.appearance.radius.none' },
  { value: 0.25, labelKey: 'settings.appearance.radius.small' },
  { value: 0.5, labelKey: 'settings.appearance.radius.medium' },
  { value: 0.75, labelKey: 'settings.appearance.radius.large' },
  { value: 1, labelKey: 'settings.appearance.radius.extraLarge' },
]

export const findAccentColor = (key: AccentColorKey): AccentColorOption =>
  accentColorOptions.find((option) => option.key === key) ?? accentColorOptions[0]!
