<script setup lang="ts">
import { ColorPaletteOutline, GridOutline, SettingsOutline } from '@vicons/ionicons5'
import { NIcon } from 'naive-ui'

import type { SettingsTab } from '@/types'

defineOptions({ name: 'SystemSettingsTabs' })

const props = defineProps<{ modelValue: SettingsTab }>()
const emit = defineEmits<{ 'update:modelValue': [value: SettingsTab] }>()

const tabs = [
  { value: 'appearance' as const, label: '外观', icon: ColorPaletteOutline },
  { value: 'layout' as const, label: '布局', icon: GridOutline },
  { value: 'general' as const, label: '通用', icon: SettingsOutline },
]

const selectTab = (tab: SettingsTab): void => {
  emit('update:modelValue', tab)
}
</script>

<template>
  <nav class="settings-tabs" aria-label="偏好设置分类" role="tablist">
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
      <span>{{ tab.label }}</span>
    </button>
  </nav>
</template>

<style scoped>
.settings-tabs {
  display: flex;
  width: 100%;
  gap: 4px;
  padding: 4px;
  border: 1px solid var(--app-color-border);
  border-radius: 10px;
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
  border-radius: 7px;
  background: transparent;
  cursor: pointer;
  font: inherit;
  font-size: 14px;
  transition:
    color 0.2s ease,
    background 0.2s ease,
    box-shadow 0.2s ease;
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
