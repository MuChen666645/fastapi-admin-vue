import lottie, {
  type AnimationConfigWithData,
  type AnimationItem,
  type RendererType,
} from 'lottie-web'

import type { LottieAnimationOptions } from '@/types'

type LottieAnimationHandle = Pick<AnimationItem, 'destroy' | 'pause' | 'play'>

export const loadLottieAnimation = (
  container: Element,
  animationData: object,
  options: LottieAnimationOptions = {},
): AnimationItem => {
  const { autoplay = true, loop = true, renderer = 'svg' } = options
  const animationConfig: AnimationConfigWithData<RendererType> = {
    animationData,
    autoplay,
    container,
    loop,
    renderer,
  }

  return lottie.loadAnimation(animationConfig)
}

export const playLottieAnimation = (animation: LottieAnimationHandle | null): void => {
  animation?.play()
}

export const pauseLottieAnimation = (animation: LottieAnimationHandle | null): void => {
  animation?.pause()
}

export const destroyLottieAnimation = (animation: LottieAnimationHandle | null): void => {
  animation?.destroy()
}
