<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'

import carLoadingAnimation from '@/assets/lottie/car-loading3-data.json'
import { useLocale, useLottie } from '@/hooks'
import { useRouteLoadingStore } from '@/stores/modules/route-loading'
import { usePreferencesStore } from '@/stores'

defineOptions({ name: 'ContentLoading' })

const routeLoading = useRouteLoadingStore()
const preferences = usePreferencesStore()
const { t } = useLocale()
const animationContainer = ref<HTMLElement | null>(null)
const isVisible = computed(
  () => preferences.loadingAnimation && routeLoading.visible && routeLoading.scope === 'content',
)
const { pause, play } = useLottie(animationContainer, carLoadingAnimation)

watch(isVisible, (visible) => {
  if (visible) {
    play()
    return
  }

  pause()
})

onMounted(() => {
  if (isVisible.value) {
    play()
  }
})

onBeforeUnmount(() => {
  pause()
})
</script>

<template>
  <div
    v-show="isVisible"
    class="content-loading"
    data-testid="content-loading"
    role="status"
    :aria-label="t('app.loading.content')"
    aria-live="polite"
    :aria-hidden="!isVisible"
  >
    <div ref="animationContainer" class="content-loading__animation" aria-hidden="true" />
  </div>
</template>

<style scoped>
.content-loading {
  position: absolute;
  z-index: 20;
  inset: 0;
  display: grid;
  place-items: center;
  background: var(--app-color-page);
}

.content-loading__animation {
  width: min(42vw, 260px);
  aspect-ratio: 1;
}

@media (width <= 480px) {
  .content-loading__animation {
    width: min(58vw, 220px);
  }
}

@media (prefers-reduced-motion: reduce) {
  .content-loading__animation {
    opacity: 0.75;
  }
}
</style>
