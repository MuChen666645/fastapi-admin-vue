import type { TranslationKey } from './system-config'

export interface ErrorPageProps {
  code: string
  titleKey: TranslationKey
  descriptionKey: TranslationKey
  animationData: object
}
