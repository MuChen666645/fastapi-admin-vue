<script setup lang="ts">
import { ref, watch } from 'vue'
import {
  CheckmarkOutline,
  ColorPaletteOutline,
  ContrastOutline,
  MoonOutline,
  SunnyOutline,
} from '@vicons/ionicons5'
import { NIcon, NInputNumber, NSwitch } from 'naive-ui'

import { useTheme } from '@/hooks/useTheme'

import type { ThemeMode } from './types'

defineOptions({ name: 'AppearanceSettings' })

const props = defineProps<{ resetKey: number }>()

const themeModes = [
  {
    value: 'light' as const,
    label: '浅色',
    description: '明亮清晰的工作环境',
    icon: SunnyOutline,
  },
  {
    value: 'dark' as const,
    label: '深色',
    description: '适合低光环境使用',
    icon: MoonOutline,
  },
  {
    value: 'system' as const,
    label: '跟随系统',
    description: '根据系统设置自动切换',
    icon: ContrastOutline,
  },
] as const

const accentColors = [
  { key: 'blue', value: '#6c7ce5', name: '默认蓝' },
  { key: 'violet', value: '#7367f0', name: '紫罗兰' },
  { key: 'rose', value: '#e94b78', name: '樱花粉' },
  { key: 'amber', value: '#e7ad38', name: '柠檬黄' },
  { key: 'green', value: '#18b887', name: '浅绿色' },
  { key: 'slate', value: '#34445d', name: '石板灰' },
] as const

const radiusOptions = [0, 0.25, 0.5, 0.75, 1]
const { isDarkMode, toggleTheme } = useTheme()
const selectedTheme = ref<ThemeMode>(isDarkMode.value ? 'dark' : 'light')
const selectedAccent = ref('#6c7ce5')
const selectedRadius = ref(0.5)
const fontSize = ref<number | null>(16)
const colorWeakMode = ref(false)
const grayscaleMode = ref(false)

const selectTheme = (mode: ThemeMode): void => {
  selectedTheme.value = mode
  const shouldUseDark =
    mode === 'dark' ||
    (mode === 'system' &&
      typeof window !== 'undefined' &&
      window.matchMedia('(prefers-color-scheme: dark)').matches)

  if (shouldUseDark !== isDarkMode.value) {
    toggleTheme()
  }
}

const selectAccent = (color: string): void => {
  selectedAccent.value = color
  if (typeof document === 'undefined') {
    return
  }

  document.documentElement.style.setProperty('--app-color-primary', color)
  document.documentElement.style.setProperty('--app-color-primary-dark', color)
}

const resetAppearance = (): void => {
  selectedTheme.value = 'light'
  selectedRadius.value = 0.5
  fontSize.value = 16
  colorWeakMode.value = false
  grayscaleMode.value = false
  selectAccent('#6c7ce5')

  if (isDarkMode.value) {
    toggleTheme()
  }
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
        <h2>外观设置</h2>
        <p>调整界面的主题、颜色和文字显示方式</p>
      </div>
    </div>

    <div class="settings-section">
      <div class="section-heading">
        <h3>主题</h3>
        <p>选择你喜欢的界面主题</p>
      </div>
      <div class="theme-grid">
        <button
          v-for="mode in themeModes"
          :key="mode.value"
          type="button"
          class="theme-choice"
          :class="{ 'theme-choice--active': selectedTheme === mode.value }"
          :aria-pressed="selectedTheme === mode.value"
          @click="selectTheme(mode.value)"
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
              {{ mode.label }}
            </span>
            <span class="theme-choice__description">{{ mode.description }}</span>
          </span>
          <span v-if="selectedTheme === mode.value" class="choice-check" aria-hidden="true">
            <NIcon :size="13"><CheckmarkOutline /></NIcon>
          </span>
        </button>
      </div>
    </div>

    <div class="settings-section">
      <div class="section-heading">
        <h3>主题色</h3>
        <p>选择应用的主要强调色</p>
      </div>
      <div class="accent-grid">
        <button
          v-for="color in accentColors"
          :key="color.key"
          type="button"
          class="accent-choice"
          :class="{ 'accent-choice--active': selectedAccent === color.value }"
          :aria-label="color.name"
          :title="color.name"
          @click="selectAccent(color.value)"
        >
          <span class="accent-swatch" :class="`accent-swatch--${color.key}`">
            <NIcon v-if="selectedAccent === color.value" :size="17" aria-hidden="true">
              <CheckmarkOutline />
            </NIcon>
          </span>
          <span>{{ color.name }}</span>
        </button>
      </div>
    </div>

    <div class="settings-section settings-section--split">
      <div class="setting-row setting-row--stacked">
        <div class="setting-copy">
          <h3>圆角</h3>
          <p>调整卡片、按钮和输入框的圆角大小</p>
        </div>
        <div class="radius-options" role="radiogroup" aria-label="圆角大小">
          <button
            v-for="radius in radiusOptions"
            :key="radius"
            type="button"
            class="radius-option"
            :class="{ 'radius-option--active': selectedRadius === radius }"
            :aria-checked="selectedRadius === radius"
            role="radio"
            @click="selectedRadius = radius"
          >
            {{ radius }}
          </button>
        </div>
      </div>
      <div class="setting-row setting-row--stacked">
        <div class="setting-copy">
          <h3>字体大小</h3>
          <p>调整全局界面的基础字体大小</p>
        </div>
        <div class="font-size-control">
          <NInputNumber v-model:value="fontSize" :min="12" :max="20" :step="1" size="small">
            <template #suffix>px</template>
          </NInputNumber>
        </div>
      </div>
    </div>

    <div class="settings-section">
      <div class="section-heading">
        <h3>其它</h3>
        <p>辅助显示选项</p>
      </div>
      <div class="setting-list">
        <div class="setting-row">
          <div class="setting-copy">
            <h3>色弱模式</h3>
            <p>优化颜色对比，提升信息辨识度</p>
          </div>
          <NSwitch v-model:value="colorWeakMode" aria-label="色弱模式" />
        </div>
        <div class="setting-row">
          <div class="setting-copy">
            <h3>灰色模式</h3>
            <p>将页面调整为低饱和度灰色显示</p>
          </div>
          <NSwitch v-model:value="grayscaleMode" aria-label="灰色模式" />
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
  border-radius: 10px;
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
  align-items: stretch;
  gap: 12px;
  padding: 12px;
  color: var(--app-color-text);
  border: 1px solid var(--app-color-border);
  border-radius: 10px;
  background: var(--app-color-surface);
  cursor: pointer;
  font: inherit;
  text-align: left;
  transition:
    border-color 0.2s ease,
    box-shadow 0.2s ease,
    transform 0.2s ease;
}

.theme-choice:hover,
.theme-choice:focus-visible {
  border-color: var(--app-color-primary);
  outline: none;
  transform: translateY(-1px);
}

.theme-choice--active {
  border-color: var(--app-color-primary);
  box-shadow: 0 0 0 2px rgb(108 124 229 / 14%);
}

.theme-preview {
  display: flex;
  height: 92px;
  overflow: hidden;
  border: 1px solid var(--app-color-border);
  border-radius: 7px;
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
  border-radius: 3px;
  background: #d8dcf0;
}

.theme-preview__card {
  display: block;
  height: 34px;
  border-radius: 4px;
  background: #fff;
  box-shadow: 0 1px 3px rgb(35 43 86 / 5%);
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
  border-radius: 8px;
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
  border-radius: 7px;
}

.accent-swatch--blue {
  background: #6c7ce5;
}

.accent-swatch--violet {
  background: #7367f0;
}

.accent-swatch--rose {
  background: #e94b78;
}

.accent-swatch--amber {
  background: #e7ad38;
}

.accent-swatch--green {
  background: #18b887;
}

.accent-swatch--slate {
  background: #34445d;
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
  gap: 6px;
}

.radius-option {
  min-width: 56px;
  min-height: 34px;
  padding: 0 12px;
  color: var(--app-color-text-muted);
  border: 1px solid var(--app-color-border);
  border-radius: 6px;
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
