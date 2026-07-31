import type { RendererType } from 'lottie-web'

export type LottieAnimationOptions = Readonly<{
  renderer?: RendererType
  loop?: boolean | number
  autoplay?: boolean
}>
