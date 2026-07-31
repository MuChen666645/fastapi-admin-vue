<script setup lang="ts">
import { computed, ref } from 'vue'
import { CopyOutline, RefreshOutline, SettingsOutline } from '@vicons/ionicons5'
import { NButton, NIcon, useMessage } from 'naive-ui'

import AppearanceSettings from './components/AppearanceSettings.vue'
import GeneralSettings from './components/GeneralSettings.vue'
import LayoutSettings from './components/LayoutSettings.vue'
import SettingsTabs from './components/SettingsTabs.vue'
import type { SettingsTab } from './components/types'

defineOptions({ name: 'SystemConfigView' })

const activeTab = ref<SettingsTab>('appearance')
const resetKey = ref(0)
const message = useMessage()
const tabLabels: Record<SettingsTab, string> = {
  appearance: '外观',
  layout: '布局',
  general: '通用',
}

const activeTabLabel = computed(() => tabLabels[activeTab.value])

const resetPreferences = (): void => {
  resetKey.value += 1
  message.success('已恢复默认偏好设置')
}
</script>

<template>
  <main class="preferences-page">
    <header class="preferences-header">
      <div class="preferences-heading">
        <div class="preferences-eyebrow">
          <NIcon :size="16" aria-hidden="true"><SettingsOutline /></NIcon>
          <span>系统偏好</span>
        </div>
        <h1>偏好设置</h1>
        <p>自定义偏好设置与实时预览</p>
      </div>
      <NButton quaternary class="reset-button" @click="resetPreferences">
        <template #icon>
          <NIcon><RefreshOutline /></NIcon>
        </template>
        恢复默认
      </NButton>
    </header>

    <SettingsTabs v-model="activeTab" />

    <div class="settings-content">
      <AppearanceSettings v-show="activeTab === 'appearance'" :reset-key="resetKey" />
      <LayoutSettings v-show="activeTab === 'layout'" :reset-key="resetKey" />
      <GeneralSettings v-show="activeTab === 'general'" :reset-key="resetKey" />
    </div>

    <footer class="preferences-footer">
      <span>当前分类：{{ activeTabLabel }}</span>
      <div class="preferences-footer__actions">
        <NButton quaternary>
          <template #icon>
            <NIcon><CopyOutline /></NIcon>
          </template>
          复制偏好设置
        </NButton>
        <NButton tertiary @click="resetPreferences">恢复默认</NButton>
      </div>
    </footer>
  </main>
</template>

<style scoped>
.preferences-page {
  display: flex;
  min-height: 100%;
  flex-direction: column;
  overflow: auto;
  color: var(--app-color-text);
}

.preferences-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
  padding: 4px 0 24px;
}

.preferences-heading h1,
.preferences-heading p,
.preferences-eyebrow {
  margin: 0;
}

.preferences-eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
  color: var(--app-color-primary);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.preferences-heading h1 {
  font-size: clamp(24px, 2vw, 30px);
  font-weight: 700;
  line-height: 1.2;
}

.preferences-heading p {
  margin-top: 8px;
  color: var(--app-color-text-muted);
  font-size: 14px;
}

.reset-button {
  color: var(--app-color-text-muted);
}

.settings-content {
  min-height: 0;
  flex: 1;
}

.preferences-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-top: auto;
  padding: 16px 0 4px;
  color: var(--app-color-text-muted);
  border-top: 1px solid var(--app-color-border);
  font-size: 12px;
}

.preferences-footer__actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

@media (width <= 600px) {
  .preferences-header {
    align-items: stretch;
    flex-direction: column;
    gap: 16px;
  }

  .reset-button {
    align-self: flex-start;
  }

  .preferences-footer {
    align-items: stretch;
    flex-direction: column;
  }

  .preferences-footer__actions {
    justify-content: flex-end;
  }
}
</style>
