<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import {
  CalendarOutline,
  CheckmarkCircleOutline,
  CodeSlashOutline,
  InformationCircleOutline,
  PlayOutline,
  RefreshOutline,
} from '@vicons/ionicons5'
import { NAlert, NButton, NIcon, NInput, NSelect, NSwitch, NTag } from 'naive-ui'

import type { UtilsDemoFormat, UtilsDemoModel, UtilsDemoResult } from '@/types'
import {
  createMoment,
  formatDate,
  formatDateTime,
  formatRelativeTime,
  formatTime,
  getDateRange,
  isValidMoment,
  parseMoment,
  toISOString,
} from '@/utils'

defineOptions({ name: 'UtilsDemoView' })

const invalidText = '无法解析'
const formatPatterns: Record<UtilsDemoFormat, string> = {
  date: 'YYYY-MM-DD',
  datetime: 'YYYY-MM-DD HH:mm:ss',
  time: 'HH:mm:ss',
}
const formatLabels: Record<UtilsDemoFormat, string> = {
  date: '日期',
  datetime: '日期时间',
  time: '时间',
}

const formatOptions = Object.entries(formatLabels).map(([value, label]) => ({
  label,
  value: value as UtilsDemoFormat,
}))

const createInitialModel = (): UtilsDemoModel => ({
  value: '2026-08-05 13:14:15',
  format: 'datetime',
  strict: true,
})

const model = reactive<UtilsDemoModel>(createInitialModel())
const result = ref<UtilsDemoResult | null>(null)

const activePattern = computed(() => formatPatterns[model.format])
const resultTagType = computed(() => (result.value?.valid ? 'success' : 'error'))
const resultTagText = computed(() => (result.value?.valid ? '解析成功' : '解析失败'))

const formatParsedValue = (value: ReturnType<typeof parseMoment>): string => {
  if (!value) {
    return invalidText
  }

  if (model.format === 'date') {
    return formatDate(value)
  }

  if (model.format === 'time') {
    return formatTime(value)
  }

  return formatDateTime(value)
}

const runDemo = (): void => {
  const parsed = parseMoment(model.value, {
    format: activePattern.value,
    strict: model.strict,
  })
  const valid = isValidMoment(model.value, {
    format: activePattern.value,
    strict: model.strict,
  })
  const range = getDateRange(parsed)

  result.value = {
    valid,
    locale: createMoment().locale(),
    parsed: parsed?.format(activePattern.value) ?? invalidText,
    formatted: formatParsedValue(parsed),
    iso: toISOString(parsed, invalidText),
    range: range ? `${formatDateTime(range.start)} 至 ${formatDateTime(range.end)}` : invalidText,
    relative: formatRelativeTime(parsed, true, invalidText),
  }
}

const resetDemo = (): void => {
  Object.assign(model, createInitialModel())
  runDemo()
}

runDemo()
</script>

<template>
  <main class="utils-demo-page">
    <header class="utils-demo-header">
      <div>
        <div class="utils-demo-eyebrow">
          <NIcon :size="16" aria-hidden="true"><CodeSlashOutline /></NIcon>
          <span>工具演示 / @/utils</span>
        </div>
        <h1>工具函数</h1>
        <p>通过真实输入观察 Moment 日期工具的解析、格式化、转换和日期范围能力。</p>
      </div>
      <NTag type="info" round>纯函数工具</NTag>
    </header>

    <section class="utils-demo-panel" aria-labelledby="utils-input-title">
      <div class="utils-demo-panel-heading">
        <div>
          <h2 id="utils-input-title">日期输入</h2>
          <p>统一从 @/utils 调用，不在页面直接操作 Moment 全局配置。</p>
        </div>
        <NIcon :size="24" color="var(--app-color-primary)" aria-hidden="true">
          <CalendarOutline />
        </NIcon>
      </div>

      <div class="utils-demo-controls">
        <NInput v-model:value="model.value" clearable placeholder="请输入日期或时间" />
        <NSelect v-model:value="model.format" :options="formatOptions" />
        <div class="utils-demo-switch">
          <span>严格解析</span>
          <NSwitch v-model:value="model.strict" />
        </div>
        <div class="utils-demo-actions">
          <NButton @click="resetDemo">
            <template #icon>
              <NIcon><RefreshOutline /></NIcon>
            </template>
            重置
          </NButton>
          <NButton class="utils-demo-run" type="primary" @click="runDemo">
            <template #icon>
              <NIcon><PlayOutline /></NIcon>
            </template>
            执行工具函数
          </NButton>
        </div>
      </div>
      <div class="utils-demo-pattern">
        当前格式：<code>{{ activePattern }}</code>
      </div>
    </section>

    <div class="utils-demo-layout">
      <section class="utils-demo-panel utils-demo-result" aria-labelledby="utils-result-title">
        <div class="utils-demo-panel-heading">
          <div>
            <h2 id="utils-result-title">执行结果</h2>
            <p>结果由封装方法组合生成，失败输入不会抛出页面级异常。</p>
          </div>
          <NTag v-if="result" :type="resultTagType" round>
            <template #icon>
              <NIcon>
                <CheckmarkCircleOutline v-if="result.valid" />
                <InformationCircleOutline v-else />
              </NIcon>
            </template>
            {{ resultTagText }}
          </NTag>
        </div>

        <NAlert v-if="result && !result.valid" type="warning" :show-icon="false">
          当前输入无法按所选格式解析，请检查分隔符、日期范围或关闭严格解析后重试。
        </NAlert>

        <dl v-if="result" class="utils-demo-result-list">
          <div>
            <dt>输入解析</dt>
            <dd>{{ result.parsed }}</dd>
          </div>
          <div>
            <dt>格式化结果</dt>
            <dd>{{ result.formatted }}</dd>
          </div>
          <div>
            <dt>ISO 结果</dt>
            <dd>{{ result.iso }}</dd>
          </div>
          <div>
            <dt>当前日期范围</dt>
            <dd>{{ result.range }}</dd>
          </div>
          <div>
            <dt>相对时间</dt>
            <dd>{{ result.relative }}</dd>
          </div>
          <div>
            <dt>Locale</dt>
            <dd>
              <code>{{ result.locale }}</code>
            </dd>
          </div>
        </dl>
      </section>

      <aside class="utils-demo-aside" aria-labelledby="utils-guide-title">
        <NAlert type="info" :show-icon="false" class="utils-demo-note">
          <strong>封装边界</strong>
          <p>页面只负责组织输入和展示结果；格式、解析、locale 和空值处理由工具层统一负责。</p>
        </NAlert>

        <section class="utils-demo-panel utils-demo-guide">
          <div class="utils-demo-guide-heading">
            <NIcon :size="18" aria-hidden="true"><InformationCircleOutline /></NIcon>
            <h2 id="utils-guide-title">本页覆盖能力</h2>
          </div>
          <ul>
            <li>
              <NIcon :size="16" aria-hidden="true"><CodeSlashOutline /></NIcon>
              <span><code>parseMoment</code> 严格解析和合法性判断</span>
            </li>
            <li>
              <NIcon :size="16" aria-hidden="true"><CalendarOutline /></NIcon>
              <span>日期、日期时间、时间和 ISO 格式化</span>
            </li>
            <li>
              <NIcon :size="16" aria-hidden="true"><RefreshOutline /></NIcon>
              <span>无效输入 fallback 和日期起止范围转换</span>
            </li>
          </ul>
        </section>
      </aside>
    </div>
  </main>
</template>

<style scoped>
.utils-demo-page {
  display: grid;
  gap: 20px;
  min-width: 0;
  color: var(--app-color-text);
}

.utils-demo-header,
.utils-demo-panel-heading,
.utils-demo-guide-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.utils-demo-header h1,
.utils-demo-header p,
.utils-demo-eyebrow,
.utils-demo-panel-heading h2,
.utils-demo-panel-heading p,
.utils-demo-guide-heading h2,
.utils-demo-note p {
  margin: 0;
}

.utils-demo-eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
  color: var(--app-color-primary);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.06em;
}

.utils-demo-header h1 {
  font-size: 26px;
  line-height: 1.2;
}

.utils-demo-header p,
.utils-demo-panel-heading p {
  margin-top: 8px;
  color: var(--app-color-text-muted);
  font-size: 14px;
}

.utils-demo-panel {
  min-width: 0;
  padding: 24px;
  border: 1px solid var(--app-color-border);
  border-radius: 8px;
  background: var(--app-color-surface);
}

.utils-demo-panel-heading {
  align-items: center;
  margin-bottom: 20px;
}

.utils-demo-panel-heading h2,
.utils-demo-guide-heading h2 {
  font-size: 16px;
  line-height: 1.4;
}

.utils-demo-controls {
  display: grid;
  grid-template-columns: minmax(220px, 1.7fr) minmax(150px, 0.8fr) auto auto;
  align-items: center;
  gap: 12px;
}

.utils-demo-switch,
.utils-demo-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.utils-demo-switch {
  white-space: nowrap;
}

.utils-demo-actions {
  justify-content: flex-end;
}

.utils-demo-run {
  min-width: 132px;
}

.utils-demo-pattern {
  margin-top: 16px;
  color: var(--app-color-text-muted);
  font-size: 13px;
}

.utils-demo-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(260px, 320px);
  align-items: start;
  gap: 20px;
}

.utils-demo-result {
  overflow: hidden;
}

.utils-demo-result-list {
  display: grid;
  gap: 0;
  margin: 20px 0 0;
  border-top: 1px solid var(--app-color-border);
}

.utils-demo-result-list > div {
  display: grid;
  grid-template-columns: minmax(120px, 0.35fr) minmax(0, 1fr);
  gap: 16px;
  padding: 14px 0;
  border-bottom: 1px solid var(--app-color-border);
}

.utils-demo-result-list dt {
  color: var(--app-color-text-muted);
  font-size: 13px;
}

.utils-demo-result-list dd {
  min-width: 0;
  margin: 0;
  overflow-wrap: anywhere;
  color: var(--app-color-text);
  font-size: 14px;
}

.utils-demo-aside {
  display: grid;
  gap: 16px;
  min-width: 0;
}

.utils-demo-note {
  line-height: 1.6;
}

.utils-demo-note p {
  margin-top: 6px;
}

.utils-demo-guide {
  padding: 18px;
}

.utils-demo-guide-heading {
  align-items: center;
  justify-content: flex-start;
  color: var(--app-color-primary);
}

.utils-demo-guide-heading h2 {
  color: var(--app-color-text);
}

.utils-demo-guide ul {
  display: grid;
  gap: 14px;
  margin: 18px 0 0;
  padding: 0;
  list-style: none;
}

.utils-demo-guide li {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  color: var(--app-color-text-muted);
  font-size: 13px;
  line-height: 1.5;
}

.utils-demo-guide li .n-icon {
  flex: 0 0 auto;
  margin-top: 2px;
  color: var(--app-color-primary);
}

@media (width <= 1000px) {
  .utils-demo-controls {
    grid-template-columns: 1fr 1fr;
  }

  .utils-demo-switch,
  .utils-demo-actions {
    justify-content: flex-start;
  }
}

@media (width <= 880px) {
  .utils-demo-layout {
    grid-template-columns: 1fr;
  }
}

@media (width <= 640px) {
  .utils-demo-panel {
    padding: 16px;
  }

  .utils-demo-controls {
    grid-template-columns: 1fr;
  }

  .utils-demo-actions {
    justify-content: stretch;
  }

  .utils-demo-actions :deep(.n-button) {
    flex: 1;
  }

  .utils-demo-result-list > div {
    grid-template-columns: 1fr;
    gap: 6px;
  }
}
</style>
