<script setup lang="ts">
import { ref } from 'vue'
import { HomeOutline, RefreshOutline } from '@vicons/ionicons5'
import { NButton, NIcon } from 'naive-ui'
import { useRouter } from 'vue-router'

import { useLocale, useLottie } from '@/hooks'
import type { ErrorPageProps } from '@/types'

defineOptions({ name: 'ErrorStatePage' })

const props = defineProps<ErrorPageProps>()
const router = useRouter()
const { t } = useLocale()
const animationContainer = ref<HTMLElement | null>(null)
useLottie(animationContainer, props.animationData, { loop: true })

const handleRefresh = (): void => {
  router.go(0)
}

const handleHome = async (): Promise<void> => {
  await router.replace({ name: 'app' })
}
</script>

<template>
  <main class="error-page" :aria-labelledby="`error-title-${props.code}`">
    <div ref="animationContainer" class="error-animation" aria-hidden="true" />
    <div class="error-code" aria-hidden="true">{{ props.code }}</div>
    <h1 :id="`error-title-${props.code}`">{{ t(props.titleKey) }}</h1>
    <p>{{ t(props.descriptionKey) }}</p>
    <div class="error-actions">
      <NButton type="primary" @click="handleRefresh">
        <template #icon>
          <NIcon aria-hidden="true"><RefreshOutline /></NIcon>
        </template>
        {{ t('error.refresh') }}
      </NButton>
      <NButton secondary @click="handleHome">
        <template #icon>
          <NIcon aria-hidden="true"><HomeOutline /></NIcon>
        </template>
        {{ t('error.home') }}
      </NButton>
    </div>
  </main>
</template>

<style lang="scss" scoped>
.error-page {
  display: grid;
  min-height: 100dvh;
  place-content: center;
  justify-items: center;
  padding: 32px 24px;
  color: var(--app-color-text);
  background: var(--app-color-page);
  text-align: center;
}

.error-animation {
  width: min(42vw, 260px);
  aspect-ratio: 1;
  margin-bottom: -12px;
}

.error-code {
  color: var(--app-color-primary);
  font-size: clamp(56px, 8vw, 88px);
  font-weight: 800;
  line-height: 1;
}

.error-page h1 {
  margin: 20px 0 8px;
  font-size: 24px;
}

.error-page p {
  max-width: 520px;
  margin: 0;
  color: var(--app-color-text-muted);
  line-height: 1.7;
}

.error-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 12px;
  margin-top: 24px;
}

@media (width <= 480px) {
  .error-page {
    padding: 24px 16px;
  }

  .error-animation {
    width: min(68vw, 240px);
  }

  .error-page h1 {
    font-size: 20px;
  }
}
</style>
