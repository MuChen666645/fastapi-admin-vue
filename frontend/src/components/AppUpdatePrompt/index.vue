<script setup lang="ts">
import { RefreshOutline } from '@vicons/ionicons5'
import { NAlert, NButton, NIcon } from 'naive-ui'
import { ref, toRef, watch } from 'vue'

import { useAppUpdate, useLocale } from '@/hooks'
import { usePreferencesStore } from '@/stores'

defineOptions({ name: 'AppUpdatePrompt' })

const preferences = usePreferencesStore()
const { t } = useLocale()
const dismissed = ref(false)
const { hasUpdate, reload } = useAppUpdate({
  enabled: toRef(preferences, 'autoUpdate'),
})

watch(hasUpdate, (available, previousAvailable) => {
  if (available && !previousAvailable) {
    dismissed.value = false
  }
})

const dismiss = (): void => {
  dismissed.value = true
}
</script>

<template>
  <Transition name="app-update-prompt">
    <NAlert
      v-if="preferences.autoUpdate && hasUpdate && !dismissed"
      class="app-update-prompt"
      type="warning"
      closable
      :title="t('appUpdate.title')"
      @close="dismiss"
    >
      <div class="app-update-prompt__content">
        <span>{{ t('appUpdate.description') }}</span>
        <NButton type="primary" size="small" @click="reload">
          <template #icon>
            <NIcon aria-hidden="true"><RefreshOutline /></NIcon>
          </template>
          {{ t('appUpdate.reload') }}
        </NButton>
      </div>
    </NAlert>
  </Transition>
</template>

<style lang="scss" scoped>
.app-update-prompt {
  position: fixed;
  z-index: 3000;
  top: 16px;
  right: 16px;
  width: min(420px, calc(100vw - 32px));
  box-shadow: 0 8px 24px rgb(0 0 0 / 12%);
}

.app-update-prompt__content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.app-update-prompt-enter-active,
.app-update-prompt-leave-active {
  transition:
    opacity 180ms ease,
    transform 180ms ease;
}

.app-update-prompt-enter-from,
.app-update-prompt-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

@media (width <= 480px) {
  .app-update-prompt {
    top: 12px;
    right: 12px;
    width: calc(100vw - 24px);
  }

  .app-update-prompt__content {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
