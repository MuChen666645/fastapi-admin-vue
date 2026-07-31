import type { AnimationItem, RendererType } from 'lottie-web'

export type LottieAnimationOptions = Readonly<{
  renderer?: RendererType
  loop?: boolean | number
  autoplay?: boolean
}>

export type LottieAnimationHandle = Pick<AnimationItem, 'destroy' | 'pause' | 'play'>
