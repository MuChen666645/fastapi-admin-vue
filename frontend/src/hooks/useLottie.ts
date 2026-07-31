import { onBeforeUnmount, onMounted, readonly, shallowRef, type Ref } from 'vue'
import type { AnimationItem } from 'lottie-web'

import {
  destroyLottieAnimation,
  loadLottieAnimation,
  pauseLottieAnimation,
  playLottieAnimation,
} from '@/utils/lottie'
import type { LottieAnimationOptions } from '@/types'

export const useLottie = (
  containerRef: Ref<HTMLElement | null>,
  animationData: object,
  options: LottieAnimationOptions = {},
) => {
  const animation = shallowRef<AnimationItem | null>(null)

  const load = (): void => {
    if (animation.value || !containerRef.value) {
      return
    }

    animation.value = loadLottieAnimation(containerRef.value, animationData, options)
  }

  const play = (): void => {
    playLottieAnimation(animation.value)
  }

  const pause = (): void => {
    pauseLottieAnimation(animation.value)
  }

  const destroy = (): void => {
    destroyLottieAnimation(animation.value)
    animation.value = null
  }

  onMounted(load)
  onBeforeUnmount(destroy)

  return {
    animation: readonly(animation),
    destroy,
    load,
    pause,
    play,
  }
}
