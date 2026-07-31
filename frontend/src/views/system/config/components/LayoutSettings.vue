<script setup lang="ts">
import { ref, watch } from 'vue'
import { GridOutline } from '@vicons/ionicons5'
import { NIcon, NSwitch } from 'naive-ui'

import type { ContentWidth } from './types'

defineOptions({ name: 'LayoutSettings' })

const props = defineProps<{ resetKey: number }>()


const contentWidth = ref<ContentWidth>('full')
const showSidebar = ref(true)
const showTabs = ref(true)
const showBreadcrumb = ref(true)
const showFooter = ref(true)

const resetLayout = (): void => {
  contentWidth.value = 'full'
  showSidebar.value = true
  showTabs.value = true
  showBreadcrumb.value = true
  showFooter.value = true
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
        <h2>布局设置</h2>
        <p>选择导航布局和内容区的显示方式</p>
      </div>
    </div>

    <div class="settings-section">
      <div class="section-heading">
        <h3>内容区</h3>
        <p>调整工作区的宽度和辅助导航</p>
      </div>
      <div class="segmented-control" role="radiogroup" aria-label="内容区宽度">
        <button
          type="button"
          :class="{ 'segmented-control__option--active': contentWidth === 'full' }"
          class="segmented-control__option"
          role="radio"
          :aria-checked="contentWidth === 'full'"
          @click="contentWidth = 'full'"
        >
          全屏内容
        </button>
        <button
          type="button"
          :class="{ 'segmented-control__option--active': contentWidth === 'centered' }"
          class="segmented-control__option"
          role="radio"
          :aria-checked="contentWidth === 'centered'"
          @click="contentWidth = 'centered'"
        >
          居中内容
        </button>
      </div>
      <div class="setting-list">
        <div class="setting-row">
          <div class="setting-copy">
            <h3>显示侧边栏</h3>
            <p>保留主导航入口，方便快速切换模块</p>
          </div>
          <NSwitch v-model:value="showSidebar" aria-label="显示侧边栏" />
        </div>
        <div class="setting-row">
          <div class="setting-copy">
            <h3>显示标签页</h3>
            <p>在内容区上方保留多页面标签导航</p>
          </div>
          <NSwitch v-model:value="showTabs" aria-label="显示标签页" />
        </div>
        <div class="setting-row">
          <div class="setting-copy">
            <h3>显示面包屑</h3>
            <p>在页面标题附近显示当前访问路径</p>
          </div>
          <NSwitch v-model:value="showBreadcrumb" aria-label="显示面包屑" />
        </div>
        <div class="setting-row">
          <div class="setting-copy">
            <h3>显示底部信息</h3>
            <p>在内容区底部保留版本和版权信息</p>
          </div>
          <NSwitch v-model:value="showFooter" aria-label="显示底部信息" />
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

.section-heading h3,
.setting-copy h3 {
  font-size: 15px;
  font-weight: 700;
}

.layout-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.layout-choice {
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

.layout-choice:hover,
.layout-choice:focus-visible {
  border-color: var(--app-color-primary);
  outline: none;
  transform: translateY(-1px);
}

.layout-choice--active {
  border-color: var(--app-color-primary);
  box-shadow: 0 0 0 2px rgb(108 124 229 / 14%);
}

.layout-preview {
  display: flex;
  height: 92px;
  overflow: hidden;
  border: 1px solid var(--app-color-border);
  border-radius: 7px;
}

.layout-preview__nav {
  width: 24%;
  flex: 0 0 24%;
  background: #cfd6ff;
}

.layout-preview__content {
  display: grid;
  flex: 1;
  gap: 6px;
  padding: 8px;
  background: #f7f8fb;
}

.layout-preview__line {
  display: block;
  height: 8px;
  border-radius: 3px;
  background: #d8dcf0;
}

.layout-preview__block {
  display: block;
  height: 34px;
  border-radius: 4px;
  background: #fff;
  box-shadow: 0 1px 3px rgb(35 43 86 / 5%);
}

.layout-preview--top {
  flex-direction: column;
}

.layout-preview--top .layout-preview__nav {
  width: 100%;
  height: 18%;
  flex-basis: 18%;
}

.layout-preview--mix .layout-preview__nav {
  width: 30%;
  flex-basis: 30%;
  border-right: 5px solid #eef0ff;
}

.layout-choice__title {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  font-size: 14px;
  font-weight: 700;
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

.segmented-control {
  display: flex;
  gap: 6px;
  margin-bottom: 8px;
}

.segmented-control__option {
  min-width: 86px;
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

.segmented-control__option:hover,
.segmented-control__option:focus-visible,
.segmented-control__option--active {
  color: #fff;
  border-color: var(--app-color-primary);
  background: var(--app-color-primary);
  outline: none;
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
  .layout-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (width <= 600px) {
  .layout-grid {
    grid-template-columns: 1fr;
  }
}
</style>
