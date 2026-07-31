<script setup lang="ts">
import { ref, watch } from 'vue'
import { CheckmarkOutline, InformationCircleOutline, SettingsOutline } from '@vicons/ionicons5'
import { NIcon, NSelect, NSwitch } from 'naive-ui'

defineOptions({ name: 'GeneralSettings' })

const props = defineProps<{ resetKey: number }>()

const languageOptions = [
  { label: '简体中文', value: 'zh-CN' },
  { label: 'English', value: 'en-US' },
]
const timezoneOptions = [
  { label: 'Asia/Shanghai (GMT+8)', value: 'Asia/Shanghai' },
  { label: 'UTC (GMT+0)', value: 'UTC' },
  { label: 'America/Los_Angeles (GMT-8)', value: 'America/Los_Angeles' },
]

const language = ref('zh-CN')
const timezone = ref('Asia/Shanghai')
const dynamicTitle = ref(true)
const watermark = ref(false)
const autoUpdate = ref(true)
const pageTransition = ref(true)
const loadingAnimation = ref(true)

const resetGeneral = (): void => {
  language.value = 'zh-CN'
  timezone.value = 'Asia/Shanghai'
  dynamicTitle.value = true
  watermark.value = false
  autoUpdate.value = true
  pageTransition.value = true
  loadingAnimation.value = true
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
        <h2>通用设置</h2>
        <p>配置语言、时区和页面交互偏好</p>
      </div>
    </div>

    <div class="settings-section">
      <div class="section-heading">
        <h3>基础设置</h3>
        <p>这些设置会影响整个管理后台</p>
      </div>
      <div class="form-grid">
        <label class="form-field">
          <span>语言</span>
          <NSelect v-model:value="language" :options="languageOptions" />
        </label>
        <label class="form-field">
          <span>时区</span>
          <NSelect v-model:value="timezone" :options="timezoneOptions" />
        </label>
      </div>
      <div class="setting-list">
        <div class="setting-row">
          <div class="setting-copy">
            <h3>动态标题</h3>
            <p>根据当前页面自动更新浏览器标签标题</p>
          </div>
          <NSwitch v-model:value="dynamicTitle" aria-label="动态标题" />
        </div>
        <div class="setting-row">
          <div class="setting-copy">
            <h3>水印</h3>
            <p>在工作区显示当前用户的身份水印</p>
          </div>
          <NSwitch v-model:value="watermark" aria-label="水印" />
        </div>
        <div class="setting-row">
          <div class="setting-copy">
            <h3>定时检查更新</h3>
            <p>定期检查前端版本并提示可用更新</p>
          </div>
          <NSwitch v-model:value="autoUpdate" aria-label="定时检查更新" />
        </div>
      </div>
    </div>

    <div class="settings-section">
      <div class="section-heading">
        <h3>动画</h3>
        <p>控制页面切换和加载反馈</p>
      </div>
      <div class="setting-list">
        <div class="setting-row">
          <div class="setting-copy">
            <h3>页面切换过渡条</h3>
            <p>路由切换时在顶部显示加载进度</p>
          </div>
          <NSwitch v-model:value="pageTransition" aria-label="页面切换过渡条" />
        </div>
         <div class="setting-row">
          <div class="setting-copy">
            <h3>页面切换 Loading</h3>
            <p>路由切换时显示全屏或内容区加载反馈</p>
          </div>
          <NSwitch v-model:value="loadingAnimation" aria-label="页面切换过渡条" />
        </div>
      </div>
    </div>

    <div class="settings-note">
      <NIcon :size="17" aria-hidden="true"><InformationCircleOutline /></NIcon>
      <span>当前设置会立即应用到本次会话，主题设置会保留到下次访问。</span>
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

.motion-previews {
  display: flex;
  gap: 16px;
  padding-top: 16px;
}

.motion-choice {
  position: relative;
  display: grid;
  width: 88px;
  height: 68px;
  place-items: center;
  border: 1px solid var(--app-color-border);
  border-radius: 8px;
  background: var(--app-color-surface);
  cursor: pointer;
}

.motion-choice--active {
  border: 2px solid var(--app-color-primary);
}

.motion-choice--active > .n-icon {
  position: absolute;
  right: 5px;
  bottom: 5px;
  color: var(--app-color-primary);
}

.motion-preview {
  display: block;
  width: 40px;
  height: 40px;
  border-radius: 7px;
  background: var(--app-color-primary);
}

.motion-preview--slide {
  width: 50px;
  transform: translateX(5px);
}

.motion-preview--scale {
  width: 34px;
  height: 34px;
}

.settings-note {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin-top: 8px;
  padding: 12px 14px;
  color: var(--app-color-text-muted);
  border-radius: 8px;
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
