<script setup lang="ts">
import { watch } from 'vue'
import { GridOutline } from '@vicons/ionicons5'
import { NIcon, NSwitch } from 'naive-ui'

import { useLocale } from '@/hooks'
import { usePreferencesStore } from '@/stores'

import type { LayoutScrollMode } from '@/types'

defineOptions({ name: 'LayoutSettings' })

const props = defineProps<{ resetKey: number }>()
const preferences = usePreferencesStore()
const { t } = useLocale()

const scrollModes: ReadonlyArray<{
  value: LayoutScrollMode
  labelKey:
    | 'settings.layout.scrollMode.content'
    | 'settings.layout.scrollMode.workspace'
    | 'settings.layout.scrollMode.sticky'
  descriptionKey:
    | 'settings.layout.scrollMode.contentDescription'
    | 'settings.layout.scrollMode.workspaceDescription'
    | 'settings.layout.scrollMode.stickyDescription'
}> = [
  {
    value: 'content',
    labelKey: 'settings.layout.scrollMode.content',
    descriptionKey: 'settings.layout.scrollMode.contentDescription',
  },
  {
    value: 'workspace',
    labelKey: 'settings.layout.scrollMode.workspace',
    descriptionKey: 'settings.layout.scrollMode.workspaceDescription',
  },
  {
    value: 'sticky',
    labelKey: 'settings.layout.scrollMode.sticky',
    descriptionKey: 'settings.layout.scrollMode.stickyDescription',
  },
]

const resetLayout = (): void => {
  preferences.reset()
}

watch(() => props.resetKey, resetLayout)
</script>

<template>
  <section class="settings-panel" role="tabpanel">
    <div class="panel-intro">
      <div class="panel-icon panel-icon--blue">
        <NIcon :size="20" aria-hidden="true"><GridOutline /></NIcon>
      </div>
      <div>
        <h2>{{ t('settings.layout.title') }}</h2>
        <p>{{ t('settings.layout.description') }}</p>
      </div>
    </div>

    <div class="settings-section">
      <div class="section-heading">
        <h3>{{ t('settings.layout.content') }}</h3>
        <p>{{ t('settings.layout.contentDescription') }}</p>
      </div>
      <div class="segmented-control" role="radiogroup" :aria-label="t('settings.layout.content')">
        <button
          type="button"
          class="segmented-control__option"
          :class="{ 'segmented-control__option--active': preferences.contentWidth === 'full' }"
          role="radio"
          :aria-checked="preferences.contentWidth === 'full'"
          @click="preferences.contentWidth = 'full'"
        >
          {{ t('settings.layout.fullWidth') }}
        </button>
        <button
          type="button"
          class="segmented-control__option"
          :class="{ 'segmented-control__option--active': preferences.contentWidth === 'centered' }"
          role="radio"
          :aria-checked="preferences.contentWidth === 'centered'"
          @click="preferences.contentWidth = 'centered'"
        >
          {{ t('settings.layout.centered') }}
        </button>
      </div>

      <div class="section-heading section-heading--scroll-mode">
        <h3>{{ t('settings.layout.scrollMode') }}</h3>
        <p>{{ t('settings.layout.scrollModeDescription') }}</p>
      </div>
      <div class="scroll-mode-grid" role="radiogroup" :aria-label="t('settings.layout.scrollMode')">
        <button
          v-for="mode in scrollModes"
          :key="mode.value"
          type="button"
          class="scroll-mode-choice"
          :class="{ 'scroll-mode-choice--active': preferences.scrollMode === mode.value }"
          role="radio"
          :aria-checked="preferences.scrollMode === mode.value"
          @click="preferences.scrollMode = mode.value"
        >
          <span class="scroll-mode-choice__title">{{ t(mode.labelKey) }}</span>
          <span class="scroll-mode-choice__description">{{ t(mode.descriptionKey) }}</span>
        </button>
      </div>

      <div class="setting-list">
        <div class="setting-row">
          <div class="setting-copy">
            <h3>{{ t('settings.layout.showSidebar') }}</h3>
            <p>{{ t('settings.layout.showSidebarDescription') }}</p>
          </div>
          <NSwitch
            v-model:value="preferences.showSidebar"
            :aria-label="t('settings.layout.showSidebar')"
          />
        </div>
        <div class="setting-row">
          <div class="setting-copy">
            <h3>{{ t('settings.layout.showTabs') }}</h3>
            <p>{{ t('settings.layout.showTabsDescription') }}</p>
          </div>
          <NSwitch
            v-model:value="preferences.showTabs"
            :aria-label="t('settings.layout.showTabs')"
          />
        </div>
        <div class="setting-row">
          <div class="setting-copy">
            <h3>{{ t('settings.layout.showBreadcrumb') }}</h3>
            <p>{{ t('settings.layout.showBreadcrumbDescription') }}</p>
          </div>
          <NSwitch
            v-model:value="preferences.showBreadcrumb"
            :aria-label="t('settings.layout.showBreadcrumb')"
          />
        </div>
        <div class="setting-row">
          <div class="setting-copy">
            <h3>{{ t('settings.layout.showFooter') }}</h3>
            <p>{{ t('settings.layout.showFooterDescription') }}</p>
          </div>
          <NSwitch
            v-model:value="preferences.showFooter"
            :aria-label="t('settings.layout.showFooter')"
          />
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
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

.panel-icon--blue {
  color: #4d6bfe;
  background: #edf1ff;
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

.section-heading--scroll-mode {
  margin-top: 28px;
}

.section-heading h3,
.setting-copy h3 {
  font-size: 15px;
  font-weight: 700;
}

.segmented-control {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 8px;
}

.segmented-control__option {
  min-width: 86px;
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

.segmented-control__option:hover,
.segmented-control__option:focus-visible,
.segmented-control__option--active {
  color: #fff;
  border-color: var(--app-color-primary);
  background: var(--app-color-primary);
  outline: none;
}

.scroll-mode-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 12px;
}

.scroll-mode-choice {
  display: grid;
  min-width: 0;
  gap: 6px;
  padding: 14px;
  color: var(--app-color-text);
  border: 1px solid var(--app-color-border);
  border-radius: var(--app-radius-md);
  background: var(--app-color-surface);
  cursor: pointer;
  font: inherit;
  text-align: left;
}

.scroll-mode-choice:hover,
.scroll-mode-choice:focus-visible,
.scroll-mode-choice--active {
  border-color: var(--app-color-primary);
  outline: none;
}

.scroll-mode-choice--active {
  box-shadow: 0 0 0 2px rgb(108 124 229 / 14%);
}

.scroll-mode-choice__title {
  font-size: 13px;
  font-weight: 700;
}

.scroll-mode-choice__description {
  color: var(--app-color-text-muted);
  font-size: 12px;
  line-height: 1.5;
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

@media (width <= 900px) {
  .scroll-mode-grid {
    grid-template-columns: 1fr;
  }
}
</style>
