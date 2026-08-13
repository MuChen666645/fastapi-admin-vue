<script setup lang="ts">
import { computed, watch } from 'vue'
import { InformationCircleOutline, SettingsOutline } from '@vicons/ionicons5'
import { NIcon, NSelect, NSwitch } from 'naive-ui'

import { useLocale } from '@/hooks'
import { usePreferencesStore } from '@/stores'

defineOptions({ name: 'SystemSettingsGeneralPanel' })

const props = defineProps<{ resetKey: number }>()
const preferences = usePreferencesStore()
const { t } = useLocale()

const languageOptions = computed(() => [
  { label: t('settings.general.language.zhCN'), value: 'zh-CN' },
  { label: t('settings.general.language.enUS'), value: 'en-US' },
])

const timezoneOptions = [
  { label: 'Asia/Shanghai (GMT+8)', value: 'Asia/Shanghai' },
  { label: 'UTC (GMT+0)', value: 'UTC' },
  { label: 'America/Los_Angeles (GMT-8)', value: 'America/Los_Angeles' },
]

const resetGeneral = (): void => {
  preferences.reset()
}

watch(() => props.resetKey, resetGeneral)
</script>

<template>
  <section class="settings-panel" role="tabpanel">
    <div class="panel-intro">
      <div class="panel-icon panel-icon--green">
        <NIcon :size="20" aria-hidden="true"><SettingsOutline /></NIcon>
      </div>
      <div>
        <h2>{{ t('settings.general.title') }}</h2>
        <p>{{ t('settings.general.description') }}</p>
      </div>
    </div>

    <div class="settings-section">
      <div class="section-heading">
        <h3>{{ t('settings.general.basic') }}</h3>
        <p>{{ t('settings.general.basicDescription') }}</p>
      </div>
      <div class="form-grid">
        <label class="form-field">
          <span>{{ t('settings.general.language') }}</span>
          <NSelect v-model:value="preferences.language" :options="languageOptions" />
        </label>
        <label class="form-field">
          <span>{{ t('settings.general.timezone') }}</span>
          <NSelect v-model:value="preferences.timezone" :options="timezoneOptions" />
        </label>
      </div>
      <div class="setting-list">
        <div class="setting-row">
          <div class="setting-copy">
            <h3>{{ t('settings.general.dynamicTitle') }}</h3>
            <p>{{ t('settings.general.dynamicTitleDescription') }}</p>
          </div>
          <NSwitch
            v-model:value="preferences.dynamicTitle"
            :aria-label="t('settings.general.dynamicTitle')"
          />
        </div>
        <div class="setting-row">
          <div class="setting-copy">
            <h3>{{ t('settings.general.watermark') }}</h3>
            <p>{{ t('settings.general.watermarkDescription') }}</p>
          </div>
          <NSwitch
            v-model:value="preferences.watermark"
            :aria-label="t('settings.general.watermark')"
          />
        </div>
        <div class="setting-row">
          <div class="setting-copy">
            <h3>{{ t('settings.general.autoUpdate') }}</h3>
            <p>{{ t('settings.general.autoUpdateDescription') }}</p>
          </div>
          <NSwitch
            v-model:value="preferences.autoUpdate"
            :aria-label="t('settings.general.autoUpdate')"
          />
        </div>
      </div>
    </div>

    <div class="settings-section">
      <div class="section-heading">
        <h3>{{ t('settings.general.animation') }}</h3>
        <p>{{ t('settings.general.animationDescription') }}</p>
      </div>
      <div class="setting-list">
        <div class="setting-row">
          <div class="setting-copy">
            <h3>{{ t('settings.general.pageTransition') }}</h3>
            <p>{{ t('settings.general.pageTransitionDescription') }}</p>
          </div>
          <NSwitch
            v-model:value="preferences.pageTransition"
            :aria-label="t('settings.general.pageTransition')"
          />
        </div>
        <div class="setting-row">
          <div class="setting-copy">
            <h3>{{ t('settings.general.loadingAnimation') }}</h3>
            <p>{{ t('settings.general.loadingAnimationDescription') }}</p>
          </div>
          <NSwitch
            v-model:value="preferences.loadingAnimation"
            :aria-label="t('settings.general.loadingAnimation')"
          />
        </div>
      </div>
    </div>

    <div class="settings-note">
      <NIcon :size="17" aria-hidden="true"><InformationCircleOutline /></NIcon>
      <span>{{ t('settings.general.note') }}</span>
    </div>
  </section>
</template>

<style lang="scss" scoped>
.settings-panel {
  padding: 32px 0 48px;
}

.panel-intro {
  display: flex;
  align-items: center;
  gap: 14px;
  padding-bottom: 28px;
}

.panel-icon {
  display: grid;
  width: 42px;
  height: 42px;
  flex: 0 0 auto;
  place-items: center;
  border-radius: var(--app-radius-lg);
}

.panel-icon--green {
  color: #18a058;
  background: #eaf9f1;
}

.panel-intro h2,
.panel-intro p,
.section-heading h3,
.section-heading p,
.setting-copy h3,
.setting-copy p {
  margin: 0;
}

.panel-intro h2 {
  font-size: 20px;
  font-weight: 700;
}

.panel-intro p,
.section-heading p,
.setting-copy p {
  margin-top: 5px;
  color: var(--app-color-text-muted);
  font-size: 13px;
  line-height: 1.5;
}

.settings-section {
  padding: 28px 0;
  border-top: 1px solid var(--app-color-border);
}

.section-heading {
  margin-bottom: 18px;
}

.section-heading h3,
.setting-copy h3 {
  font-size: 15px;
  font-weight: 700;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20px;
  padding-bottom: 12px;
}

.form-field {
  display: grid;
  gap: 8px;
  color: var(--app-color-text);
  font-size: 13px;
  font-weight: 600;
}

.setting-row {
  display: flex;
  min-height: 52px;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  padding: 12px 0;
}

.setting-copy {
  min-width: 0;
}

.setting-list {
  display: grid;
  gap: 4px;
}

.setting-list .setting-row + .setting-row {
  border-top: 1px solid var(--app-color-border);
}

.settings-note {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin-top: 8px;
  padding: 12px 14px;
  color: var(--app-color-text-muted);
  border-radius: var(--app-radius-md);
  background: var(--app-color-surface-muted);
  font-size: 12px;
  line-height: 1.5;
}

@media (width <= 600px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
