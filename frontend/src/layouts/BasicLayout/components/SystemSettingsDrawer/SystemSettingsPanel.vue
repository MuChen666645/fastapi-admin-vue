<script setup lang="ts">
import { computed, ref } from 'vue'
import { CopyOutline } from '@vicons/ionicons5'
import { NButton, NIcon, useMessage } from 'naive-ui'

import { useLocale } from '@/hooks'
import { usePreferencesStore } from '@/stores'

import AppearanceSettings from './components/AppearanceSettings.vue'
import GeneralSettings from './components/GeneralSettings.vue'
import LayoutSettings from './components/LayoutSettings.vue'
import SettingsTabs from './components/SettingsTabs.vue'

import type { SettingsTab } from '@/types'

defineOptions({ name: 'SystemSettingsDrawerPanel' })

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
  <section class="preferences-page">
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
  </section>
</template>

<style lang="scss" scoped>
.preferences-page {
  display: flex;
  min-height: 100%;
  flex-direction: column;
  overflow: auto;
  -ms-overflow-style: none;
  color: var(--app-color-text);
  scrollbar-width: none;
}

.preferences-page::-webkit-scrollbar {
  width: 0;
  height: 0;
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
  .preferences-footer {
    align-items: stretch;
    flex-direction: column;
  }

  .preferences-footer__actions {
    justify-content: flex-end;
  }
}
</style>
