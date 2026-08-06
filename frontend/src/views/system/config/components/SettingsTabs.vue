<script setup lang="ts">
import { ColorPaletteOutline, GridOutline, SettingsOutline } from '@vicons/ionicons5'
import { NIcon } from 'naive-ui'

import { useLocale } from '@/hooks'

import type { SettingsTab, TranslationKey } from '@/types'

defineOptions({ name: 'SystemSettingsTabs' })

const props = defineProps<{ modelValue: SettingsTab }>()
const emit = defineEmits<{ 'update:modelValue': [value: SettingsTab] }>()
const { t } = useLocale()

const tabs: ReadonlyArray<{
  value: SettingsTab
  labelKey: Extract<TranslationKey, `settings.tab.${string}`>
  icon: typeof ColorPaletteOutline
}> = [
  { value: 'appearance', labelKey: 'settings.tab.appearance', icon: ColorPaletteOutline },
  { value: 'layout', labelKey: 'settings.tab.layout', icon: GridOutline },
  { value: 'general', labelKey: 'settings.tab.general', icon: SettingsOutline },
]

const selectTab = (tab: SettingsTab): void => {
  emit('update:modelValue', tab)
}
</script>

<template>
  <nav class="settings-tabs" :aria-label="t('settings.title')" role="tablist">
    <button
      v-for="tab in tabs"
      :key="tab.value"
      type="button"
      class="settings-tab"
      :class="{ 'settings-tab--active': props.modelValue === tab.value }"
      role="tab"
      :aria-selected="props.modelValue === tab.value"
      @click="selectTab(tab.value)"
    >
      <NIcon :size="17" aria-hidden="true"><component :is="tab.icon" /></NIcon>
      <span>{{ t(tab.labelKey) }}</span>
    </button>
  </nav>
</template>

<style lang="scss" scoped>
.settings-tabs {
  display: flex;
  width: 100%;
  gap: 4px;
  padding: 4px;
  border: 1px solid var(--app-color-border);
  border-radius: var(--app-radius-lg);
  background: var(--app-color-surface-muted);
}

.settings-tab {
  display: inline-flex;
  min-height: 38px;
  flex: 1;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 0 16px;
  color: var(--app-color-text-muted);
  border: 0;
  border-radius: var(--app-radius-sm);
  background: transparent;
  cursor: pointer;
  font: inherit;
  font-size: 14px;
}

.settings-tab:hover,
.settings-tab:focus-visible {
  color: var(--app-color-primary);
  outline: none;
}

.settings-tab--active {
  color: var(--app-color-primary);
  background: var(--app-color-surface);
  box-shadow: 0 1px 4px rgb(35 43 86 / 8%);
  font-weight: 700;
}

@media (width <= 600px) {
  .settings-tab {
    padding: 0 8px;
  }

  .settings-tab span {
    font-size: 12px;
  }
}
</style>
