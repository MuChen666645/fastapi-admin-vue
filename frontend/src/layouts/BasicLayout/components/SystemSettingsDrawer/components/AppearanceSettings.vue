<script setup lang="ts">
import { computed, watch } from 'vue'
import {
  CheckmarkOutline,
  ColorPaletteOutline,
  ContrastOutline,
  MoonOutline,
  SunnyOutline,
} from '@vicons/ionicons5'
import { NIcon, NInputNumber, NSwitch } from 'naive-ui'

import { useLocale } from '@/hooks'
import { usePreferencesStore } from '@/stores'
import { accentColorOptions, radiusOptions } from '@/utils'

import type { ThemeMode } from '@/types'

defineOptions({ name: 'SystemSettingsAppearancePanel' })

const props = defineProps<{ resetKey: number }>()
const preferences = usePreferencesStore()
const { t } = useLocale()

const themeModes: ReadonlyArray<{
  value: ThemeMode
  labelKey: 'settings.appearance.light' | 'settings.appearance.dark' | 'settings.appearance.system'
  descriptionKey:
    | 'settings.appearance.lightDescription'
    | 'settings.appearance.darkDescription'
    | 'settings.appearance.systemDescription'
  icon: typeof SunnyOutline
}> = [
  {
    value: 'light',
    labelKey: 'settings.appearance.light',
    descriptionKey: 'settings.appearance.lightDescription',
    icon: SunnyOutline,
  },
  {
    value: 'dark',
    labelKey: 'settings.appearance.dark',
    descriptionKey: 'settings.appearance.darkDescription',
    icon: MoonOutline,
  },
  {
    value: 'system',
    labelKey: 'settings.appearance.system',
    descriptionKey: 'settings.appearance.systemDescription',
    icon: ContrastOutline,
  },
]

const selectedTheme = computed({
  get: () => preferences.themeMode,
  set: (value: ThemeMode) => {
    preferences.themeMode = value
  },
})

const resetAppearance = (): void => {
  preferences.reset()
}

watch(() => props.resetKey, resetAppearance)
</script>

<template>
  <section class="settings-panel" role="tabpanel">
    <div class="panel-intro">
      <div class="panel-icon panel-icon--purple">
        <NIcon :size="20" aria-hidden="true"><ColorPaletteOutline /></NIcon>
      </div>
      <div>
        <h2>{{ t('settings.appearance.title') }}</h2>
        <p>{{ t('settings.appearance.description') }}</p>
      </div>
    </div>

    <div class="settings-section">
      <div class="section-heading">
        <h3>{{ t('settings.appearance.theme') }}</h3>
        <p>{{ t('settings.appearance.themeDescription') }}</p>
      </div>
      <div class="theme-grid">
        <button
          v-for="mode in themeModes"
          :key="mode.value"
          type="button"
          class="theme-choice"
          :class="{ 'theme-choice--active': selectedTheme === mode.value }"
          :aria-pressed="selectedTheme === mode.value"
          @click="selectedTheme = mode.value"
        >
          <span class="theme-preview" :class="`theme-preview--${mode.value}`">
            <span class="theme-preview__sidebar" />
            <span class="theme-preview__body">
              <span class="theme-preview__topbar" />
              <span class="theme-preview__card" />
              <span class="theme-preview__card theme-preview__card--short" />
            </span>
          </span>
          <span class="theme-choice__meta">
            <span class="theme-choice__title">
              <NIcon :size="16" aria-hidden="true"><component :is="mode.icon" /></NIcon>
              {{ t(mode.labelKey) }}
            </span>
            <span class="theme-choice__description">{{ t(mode.descriptionKey) }}</span>
          </span>
          <span v-if="selectedTheme === mode.value" class="choice-check" aria-hidden="true">
            <NIcon :size="13"><CheckmarkOutline /></NIcon>
          </span>
        </button>
      </div>
    </div>

    <div class="settings-section">
      <div class="section-heading">
        <h3>{{ t('settings.appearance.accent') }}</h3>
        <p>{{ t('settings.appearance.accentDescription') }}</p>
      </div>
      <div class="accent-grid">
        <button
          v-for="color in accentColorOptions"
          :key="color.key"
          type="button"
          class="accent-choice"
          :class="{ 'accent-choice--active': preferences.accentColor === color.key }"
          :aria-label="t(color.nameKey)"
          :title="t(color.nameKey)"
          @click="preferences.accentColor = color.key"
        >
          <span class="accent-swatch" :style="{ backgroundColor: color.light }">
            <NIcon v-if="preferences.accentColor === color.key" :size="17" aria-hidden="true">
              <CheckmarkOutline />
            </NIcon>
          </span>
          <span>{{ t(color.nameKey) }}</span>
        </button>
      </div>
    </div>

    <div class="settings-section settings-section--split">
      <div class="setting-row setting-row--stacked">
        <div class="setting-copy">
          <h3>{{ t('settings.appearance.radius') }}</h3>
          <p>{{ t('settings.appearance.radiusDescription') }}</p>
        </div>
        <div class="radius-options" role="radiogroup" :aria-label="t('settings.appearance.radius')">
          <button
            v-for="radius in radiusOptions"
            :key="radius.value"
            type="button"
            class="radius-option"
            :class="{ 'radius-option--active': preferences.radiusScale === radius.value }"
            :aria-checked="preferences.radiusScale === radius.value"
            role="radio"
            @click="preferences.radiusScale = radius.value"
          >
            {{ t(radius.labelKey) }}
          </button>
        </div>
      </div>
      <div class="setting-row setting-row--stacked">
        <div class="setting-copy">
          <h3>{{ t('settings.appearance.fontSize') }}</h3>
          <p>{{ t('settings.appearance.fontSizeDescription') }}</p>
        </div>
        <div class="font-size-control">
          <NInputNumber
            v-model:value="preferences.fontSize"
            :min="12"
            :max="20"
            :step="1"
            size="small"
          >
            <template #suffix>px</template>
          </NInputNumber>
        </div>
      </div>
    </div>

    <div class="settings-section">
      <div class="section-heading">
        <h3>{{ t('settings.appearance.other') }}</h3>
        <p>{{ t('settings.appearance.otherDescription') }}</p>
      </div>
      <div class="setting-list">
        <div class="setting-row">
          <div class="setting-copy">
            <h3>{{ t('settings.appearance.colorWeak') }}</h3>
            <p>{{ t('settings.appearance.colorWeakDescription') }}</p>
          </div>
          <NSwitch
            v-model:value="preferences.colorWeakMode"
            :aria-label="t('settings.appearance.colorWeak')"
          />
        </div>
        <div class="setting-row">
          <div class="setting-copy">
            <h3>{{ t('settings.appearance.grayscale') }}</h3>
            <p>{{ t('settings.appearance.grayscaleDescription') }}</p>
          </div>
          <NSwitch
            v-model:value="preferences.grayscaleMode"
            :aria-label="t('settings.appearance.grayscale')"
          />
        </div>
      </div>
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

.panel-icon--purple {
  color: #7367f0;
  background: #f0edff;
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

.theme-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.theme-choice {
  position: relative;
  display: flex;
  min-width: 0;
  flex-direction: column;
  gap: 12px;
  padding: 12px;
  color: var(--app-color-text);
  border: 1px solid var(--app-color-border);
  border-radius: var(--app-radius-lg);
  background: var(--app-color-surface);
  cursor: pointer;
  font: inherit;
  text-align: left;
}

.theme-choice:hover,
.theme-choice:focus-visible,
.theme-choice--active {
  border-color: var(--app-color-primary);
  outline: none;
}

.theme-choice--active {
  box-shadow: 0 0 0 2px rgb(108 124 229 / 14%);
}

.theme-preview {
  display: flex;
  height: 92px;
  overflow: hidden;
  border: 1px solid var(--app-color-border);
  border-radius: var(--app-radius-sm);
}

.theme-preview__sidebar {
  width: 22%;
  flex: 0 0 22%;
  background: #e8ebff;
}

.theme-preview__body {
  display: grid;
  flex: 1;
  gap: 6px;
  padding: 8px;
  background: #f7f8fb;
}

.theme-preview__topbar {
  display: block;
  height: 8px;
  border-radius: var(--app-radius-xs);
  background: #d8dcf0;
}

.theme-preview__card {
  display: block;
  height: 34px;
  border-radius: var(--app-radius-xs);
  background: #fff;
}

.theme-preview__card--short {
  width: 68%;
  height: 18px;
}

.theme-preview--dark .theme-preview__sidebar {
  background: #303867;
}

.theme-preview--dark .theme-preview__body {
  background: #202433;
}

.theme-preview--dark .theme-preview__topbar {
  background: #4a558e;
}

.theme-preview--dark .theme-preview__card {
  background: #303650;
}

.theme-preview--system .theme-preview__sidebar {
  background: linear-gradient(180deg, #e8ebff 0 50%, #303867 50%);
}

.theme-choice__meta {
  display: grid;
  gap: 4px;
}

.theme-choice__title {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  font-size: 14px;
  font-weight: 700;
}

.theme-choice__description {
  color: var(--app-color-text-muted);
  font-size: 12px;
}

.choice-check {
  position: absolute;
  top: 10px;
  right: 10px;
  display: grid;
  width: 20px;
  height: 20px;
  place-items: center;
  color: #fff;
  border-radius: 50%;
  background: var(--app-color-primary);
}

.accent-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.accent-choice {
  display: grid;
  width: 88px;
  min-height: 76px;
  place-items: center;
  gap: 8px;
  padding: 8px;
  color: var(--app-color-text-muted);
  border: 1px solid var(--app-color-border);
  border-radius: var(--app-radius-md);
  background: var(--app-color-surface);
  cursor: pointer;
  font: inherit;
  font-size: 12px;
}

.accent-choice:hover,
.accent-choice:focus-visible,
.accent-choice--active {
  color: var(--app-color-text);
  border-color: var(--app-color-primary);
  outline: none;
}

.accent-swatch {
  display: grid;
  width: 26px;
  height: 26px;
  place-items: center;
  color: #fff;
  border-radius: var(--app-radius-sm);
}

.settings-section--split {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(280px, 0.7fr);
  gap: 32px;
}

.setting-row {
  display: flex;
  min-height: 52px;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  padding: 12px 0;
}

.setting-row--stacked {
  display: grid;
  place-content: start stretch;
  gap: 14px;
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

.radius-options {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.radius-option {
  min-width: 56px;
  min-height: 34px;
  padding: 0 12px;
  color: var(--app-color-text-muted);
  border: 1px solid var(--app-color-border);
  border-radius: var(--app-radius-sm);
  background: var(--app-color-surface);
  cursor: pointer;
  font: inherit;
  font-size: 13px;
}

.radius-option:hover,
.radius-option:focus-visible,
.radius-option--active {
  color: #fff;
  border-color: var(--app-color-primary);
  background: var(--app-color-primary);
  outline: none;
}

.font-size-control {
  max-width: 220px;
}

@media (width <= 900px) {
  .theme-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .settings-section--split {
    grid-template-columns: 1fr;
  }
}

@media (width <= 600px) {
  .theme-grid {
    grid-template-columns: 1fr;
  }
}
</style>
