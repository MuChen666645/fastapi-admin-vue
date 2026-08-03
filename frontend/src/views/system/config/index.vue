<script setup lang="ts">
import { computed, ref } from 'vue'
import { CopyOutline, RefreshOutline, SettingsOutline } from '@vicons/ionicons5'
import { NButton, NIcon, useMessage } from 'naive-ui'

import { useLocale } from '@/hooks'
import { usePreferencesStore } from '@/stores'

import AppearanceSettings from './components/AppearanceSettings.vue'
import GeneralSettings from './components/GeneralSettings.vue'
import LayoutSettings from './components/LayoutSettings.vue'
import SettingsTabs from './components/SettingsTabs.vue'

import type { SettingsTab } from '@/types'

defineOptions({ name: 'SystemConfigView' })

const activeTab = ref<SettingsTab>('appearance')
const resetKey = ref(0)
const message = useMessage()
const preferences = usePreferencesStore()
const { t } = useLocale()

const activeTabLabel = computed(() => t(`settings.tab.${activeTab.value}` as const))

const resetPreferences = (): void => {
  preferences.reset()
  resetKey.value += 1
  message.success(t('app.message.preferencesReset'))
}

const copyPreferences = async (): Promise<void> => {
  if (typeof navigator === 'undefined' || !navigator.clipboard) {
    message.error(t('app.message.preferencesCopyFailed'))
    return
  }

  try {
    await navigator.clipboard.writeText(JSON.stringify({ ...preferences.$state }, null, 2))
    message.success(t('app.message.preferencesCopied'))
  } catch {
    message.error(t('app.message.preferencesCopyFailed'))
  }
}
</script>

<template>
  <main class="preferences-page">
    <header class="preferences-header">
      <div class="preferences-heading">
        <div class="preferences-eyebrow">
          <NIcon :size="16" aria-hidden="true"><SettingsOutline /></NIcon>
          <span>{{ t('settings.eyebrow') }}</span>
        </div>
        <h1>{{ t('settings.title') }}</h1>
        <p>{{ t('settings.description') }}</p>
      </div>
      <NButton quaternary class="reset-button" @click="resetPreferences">
        <template #icon>
          <NIcon><RefreshOutline /></NIcon>
        </template>
        {{ t('settings.reset') }}
      </NButton>
    </header>

    <SettingsTabs v-model="activeTab" />

    <div class="settings-content">
      <AppearanceSettings v-show="activeTab === 'appearance'" :reset-key="resetKey" />
      <LayoutSettings v-show="activeTab === 'layout'" :reset-key="resetKey" />
      <GeneralSettings v-show="activeTab === 'general'" :reset-key="resetKey" />
    </div>

    <footer class="preferences-footer">
      <span>{{ t('settings.currentCategory').replace('{category}', activeTabLabel) }}</span>
      <div class="preferences-footer__actions">
        <NButton quaternary @click="copyPreferences">
          <template #icon>
            <NIcon><CopyOutline /></NIcon>
          </template>
          {{ t('settings.copy') }}
        </NButton>
        <NButton tertiary @click="resetPreferences">{{ t('settings.reset') }}</NButton>
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
