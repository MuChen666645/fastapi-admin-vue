<script setup lang="ts">
import { onMounted, ref } from 'vue'
import {
  LockClosedOutline,
  MoonOutline,
  PersonOutline,
  RefreshOutline,
  ShieldCheckmarkOutline,
  SunnyOutline,
} from '@vicons/ionicons5'
import { NAlert, NButton, NForm, NFormItem, NIcon, NInput, NText } from 'naive-ui'
import type { FormInst, FormRules } from 'naive-ui'
import { useRoute, useRouter } from 'vue-router'

import { fetchCaptcha } from '@/api'
import { useTheme } from '@/hooks'
import { useAuthStore } from '@/stores'
import type { LoginCredentials } from '@/types'
import { ApiError } from '@/utils/request'
import {
  clearRememberedLogin,
  getRememberedLogin,
  saveRememberedLogin,
} from '@/utils/loginPreferences'

import FramShip from '@/assets/images/login/FramShip.svg'
import Illustration1 from '@/assets/images/login/Illustration1.svg'

defineOptions({ name: 'LoginView' })

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const formRef = ref<FormInst | null>(null)
const rememberedLogin = getRememberedLogin()
const form = ref({
  identifier: rememberedLogin?.identifier ?? auth.rememberedUsername,
  password: rememberedLogin?.password ?? '',
  captcha: '',
  mfaCode: '',
  remember: rememberedLogin !== null || Boolean(auth.rememberedUsername),
})
const captchaId = ref('')
const captchaImage = ref('')
const captchaLoading = ref(false)
const submitting = ref(false)
const errorMessage = ref('')
const { isDarkMode, toggleTheme } = useTheme()

const rules: FormRules = {
  identifier: { required: true, message: '请输入用户名或手机号', trigger: ['input', 'blur'] },
  password: { required: true, message: '请输入密码', trigger: ['input', 'blur'] },
  captcha: { required: true, message: '请输入图形验证码', trigger: ['input', 'blur'] },
}

const loadCaptcha = async (): Promise<void> => {
  captchaLoading.value = true
  try {
    const captcha = await fetchCaptcha()
    captchaId.value = captcha.captcha_id
    captchaImage.value = captcha.image
    form.value.captcha = ''
  } catch {
    captchaId.value = ''
    captchaImage.value = ''
  } finally {
    captchaLoading.value = false
  }
}

const handleCaptchaRefresh = (): void => {
  if (!captchaLoading.value) {
    void loadCaptcha()
  }
}

const handleLogin = async (): Promise<void> => {
  if (!formRef.value || submitting.value) {
    return
  }

  try {
    await formRef.value.validate()
  } catch {
    return
  }

  if (!captchaId.value) {
    errorMessage.value = '验证码加载失败，请刷新后重试'
    return
  }

  submitting.value = true
  errorMessage.value = ''
  try {
    await auth.signIn(
      {
        loginType: 'username' as LoginCredentials['loginType'],
        identifier: form.value.identifier,
        password: form.value.password,
        captcha_id: captchaId.value,
        captcha: form.value.captcha,
        mfa_code: form.value.mfaCode || undefined,
      } as LoginCredentials,
      form.value.remember,
    )
    if (form.value.remember) {
      saveRememberedLogin({
        identifier: form.value.identifier,
        password: form.value.password,
      })
    } else {
      clearRememberedLogin()
    }
  } catch (error) {
    errorMessage.value =
      error instanceof ApiError
        ? error.message
        : error instanceof Error
          ? error.message
          : '登录失败，请稍后重试'
    await loadCaptcha()
    submitting.value = false
    return
  }

  try {
    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/'
    const safeRedirect =
      redirect.startsWith('/') && !redirect.startsWith('//') && redirect !== '/login'
        ? redirect
        : '/'

    await router.replace({ name: 'app' })
    if (safeRedirect !== '/') {
      await router.replace(safeRedirect)
    }
  } catch {
    errorMessage.value = '登录成功，但页面跳转失败，请刷新后重试'
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  void loadCaptcha()
})
</script>

<template>
  <main class="login-page" :class="{ 'login-page--dark': isDarkMode }">
    <!-- 左侧品牌展示区 -->
    <section class="login-brand-panel" aria-labelledby="brand-title">
      <!-- 装饰性背景渐变 -->
      <div class="brand-bg-gradient" aria-hidden="true"></div>

      <!-- 装饰性插画 -->
      <div class="brand-decoration brand-decoration--top" aria-hidden="true">
        <Illustration1 class="brand-decoration-svg" aria-hidden="true" focusable="false" />
      </div>

      <!-- Logo -->
      <header class="brand-header">
        <div class="brand-logo" aria-hidden="true">
          <NIcon :size="24"><ShieldCheckmarkOutline /></NIcon>
        </div>
        <NText class="brand-name" strong>FastApi-Admin</NText>
      </header>

      <!-- 船形插画 -->
      <div class="brand-illustration" aria-hidden="true">
        <FramShip class="brand-illustration-svg" aria-hidden="true" focusable="false" />
      </div>

      <!-- 标语 -->
      <div class="brand-copy">
        <NText id="brand-title" tag="h1" class="brand-title" strong>
          一款开箱即用的后台管理系统
        </NText>
        <NText class="brand-subtitle">基于 Vue3 + Naive UI + Vite</NText>
      </div>

      <NText class="brand-copyright">© 2026 FastApi-Admin</NText>
    </section>

    <!-- 右侧登录表单区 -->
    <section class="login-workspace" aria-labelledby="login-title">
      <!-- 顶部工具栏 -->
      <div class="workspace-topbar">
        <NButton
          quaternary
          circle
          size="small"
          class="theme-toggle"
          :aria-label="isDarkMode ? '切换浅色主题' : '切换深色主题'"
          :title="isDarkMode ? '切换浅色主题' : '切换深色主题'"
          @click="toggleTheme"
        >
          <template #icon>
            <NIcon :size="18">
              <SunnyOutline v-if="isDarkMode" />
              <MoonOutline v-else />
            </NIcon>
          </template>
        </NButton>
      </div>

      <!-- 登录卡片 -->
      <div class="login-card">
        <div class="login-heading">
          <NText id="login-title" tag="h2" class="login-title" strong>
            欢迎使用 FastApi-Admin
          </NText>
        </div>

        <NAlert v-if="errorMessage" type="error" :show-icon="false" class="login-error">
          {{ errorMessage }}
        </NAlert>

        <NForm
          ref="formRef"
          :model="form"
          :rules="rules"
          label-placement="top"
          size="large"
          class="login-form"
        >
          <NFormItem label="用户名" path="identifier">
            <NInput
              v-model:value="form.identifier"
              placeholder="请输入用户名"
              autocomplete="username"
            >
              <template #prefix>
                <NIcon :size="16" class="input-icon"><PersonOutline /></NIcon>
              </template>
            </NInput>
          </NFormItem>

          <NFormItem label="密码" path="password">
            <NInput
              v-model:value="form.password"
              type="password"
              placeholder="请输入密码"
              show-password-on="click"
              autocomplete="current-password"
            >
              <template #prefix>
                <NIcon :size="16" class="input-icon"><LockClosedOutline /></NIcon>
              </template>
            </NInput>
          </NFormItem>

          <NFormItem label="图形验证码" path="captcha">
            <div class="captcha-field">
              <NInput v-model:value="form.captcha" placeholder="请输入验证码" autocomplete="off" />
              <button
                type="button"
                class="captcha-image"
                :disabled="captchaLoading"
                aria-label="刷新图形验证码"
                title="刷新图形验证码"
                @click="handleCaptchaRefresh"
              >
                <img v-if="captchaImage" :src="captchaImage" alt="图形验证码" />
                <span v-else>
                  <NIcon :size="18"><RefreshOutline /></NIcon>
                  {{ captchaLoading ? '加载中' : '点击刷新' }}
                </span>
              </button>
            </div>
          </NFormItem>

          <NFormItem label="MFA 验证码（可选）" path="mfaCode">
            <NInput
              v-model:value="form.mfaCode"
              placeholder="启用 MFA 时填写"
              autocomplete="one-time-code"
            />
          </NFormItem>

          <div class="login-actions">
            <label class="remember-option">
              <input v-model="form.remember" type="checkbox" />
              <span>记住我</span>
            </label>
          </div>

          <NButton
            type="primary"
            block
            class="login-submit"
            :bordered="false"
            :loading="submitting"
            @click="handleLogin"
          >
            登录
          </NButton>
        </NForm>
      </div>
    </section>
  </main>
</template>

<style scoped>
.login-page {
  --login-bg: #f4f6f8;
  --login-surface: #fff;
  --login-text: #1d2b28;
  --login-muted: #72817c;
  --login-primary: #6c7ce5;
  --login-primary-dark: #5762e0;
  --login-accent: #8ea1e9;
  --login-button-bg: rgb(175 188 237 / 58%);
  --login-button-border: #aeb4cb;
  --login-input-surface: #fff;
  --login-input-border: #d5ded9;
  --login-input-border-hover: #7c89db;
  --login-input-border-focus: #7c89db;
  --login-input-focus-shadow: 0 0 0 2px rgb(124 137 219 / 18%);
  --login-card-shadow: 0 4px 41px 13px rgb(253 231 231 / 60%);
  --login-gradient-start: rgb(132 105 151 / 4%);
  --login-gradient-end: rgb(116 124 175 / 29%);
  --login-text-gradient-start: rgb(129 134 194 / 0%);
  --login-text-gradient-end: rgb(88 98 224 / 57%);

  display: grid;
  width: 100%;
  height: 100dvh;
  min-height: 560px;
  overflow: hidden;
  color: var(--login-text);
  background: var(--login-bg);
  grid-template-columns: minmax(0, 2fr) minmax(420px, 1fr);
}

/* ===== 左侧品牌展示区 ===== */
.login-brand-panel {
  position: relative;
  display: flex;
  min-height: 0;
  height: 100%;
  flex-direction: column;
  padding: 48px 6vw 36px;
  color: #fff;
  background: linear-gradient(135deg, #6c7ce5 0%, #8e9add 50%, #747caf 100%);
  overflow: hidden;
}

.brand-bg-gradient {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    135deg,
    var(--login-gradient-start) 0%,
    var(--login-gradient-end) 100%
  );
  pointer-events: none;
}

.brand-decoration {
  position: absolute;
  pointer-events: none;
  z-index: 0;
}

.brand-decoration--top {
  top: 22px;
  right: 22px;
  width: 333px;
  height: 268px;
  opacity: 0.5;
}

.brand-decoration-svg {
  display: block;
  width: 100%;
  height: 100%;
}

.brand-header {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 14px;
}

.brand-logo {
  display: grid;
  width: 42px;
  height: 42px;
  place-items: center;
  color: var(--login-primary);
  border-radius: 10px;
  background: #fff;
  box-shadow: 0 2px 8px rgb(0 0 0 / 10%);
}

.brand-name {
  color: #fff;
  font-size: 22px;
  letter-spacing: 0.5px;
}

.brand-illustration {
  position: relative;
  z-index: 1;
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 20px 0;
}

.brand-illustration-svg {
  display: block;
  width: min(100%, 650px);
  max-height: 500px;
  filter: drop-shadow(0 8px 24px rgb(0 0 0 / 15%));
}

.brand-copy {
  position: relative;
  z-index: 1;
  text-align: center;
  margin: 0 0 20px;
}

.brand-title {
  display: block;
  margin: 0;
  color: #fff;
  font-size: 36px;
  line-height: 1.3;
  text-shadow: 0 2px 12px rgb(0 0 0 / 15%);
}

.brand-subtitle {
  display: block;
  margin-top: 12px;
  color: rgb(255 255 255 / 85%);
  font-size: 18px;
}

.brand-copyright {
  position: relative;
  z-index: 1;
  color: rgb(255 255 255 / 56%);
  font-size: 12px;
  text-align: center;
}

/* ===== 右侧登录表单区 ===== */
.login-workspace {
  position: relative;
  display: flex;
  min-width: 0;
  min-height: 0;
  height: 100%;
  align-items: center;
  justify-content: center;
  padding: 64px 28px 28px;
  background: linear-gradient(135deg, #fbfcff 0%, #f0f2fa 52%, #e7ebf6 100%);
}

.workspace-topbar {
  position: absolute;
  top: 24px;
  right: 28px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 14px;
}

.theme-toggle {
  width: 36px;
  height: 36px;
  color: var(--login-muted);
}

.theme-toggle:hover,
.theme-toggle:focus-visible {
  color: var(--login-primary);
}

/* ===== 登录卡片 ===== */
.login-card {
  width: min(100%, 420px);
  max-height: calc(100dvh - 40px);
  padding: 32px 32px 24px;
  border-radius: 16px;
  background: var(--login-surface);
  box-shadow: var(--login-card-shadow);
}

.login-heading {
  text-align: center;
  margin-bottom: 20px;
}

.login-title {
  margin: 0;
  color: var(--login-primary);
  font-size: 25px;
  line-height: 1.25;
  opacity: 0.85;
}

.login-error {
  margin-bottom: 12px;
}

.login-form {
  width: 100%;
}

.input-icon {
  color: var(--login-muted);
}

.captcha-field {
  display: grid;
  width: 100%;
  grid-template-columns: minmax(0, 1fr) 124px;
  gap: 10px;
}

.captcha-image {
  display: grid;
  min-width: 0;
  height: 44px;
  padding: 0;
  place-items: center;
  overflow: hidden;
  color: var(--login-muted);
  border: 1px solid var(--login-input-border);
  border-radius: 6px;
  background: var(--login-surface);
  cursor: pointer;
  font-size: 12px;
}

.captcha-image span {
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.captcha-image:hover:not(:disabled),
.captcha-image:focus-visible {
  color: var(--login-input-border-hover);
  border-color: var(--login-input-border-hover);
  outline: none;
}

.captcha-image:disabled {
  cursor: wait;
  opacity: 0.65;
}

.captcha-image img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.login-actions {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 12px;
  margin: 0 0 16px;
}

.remember-option {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: var(--login-muted);
  font-size: 14px;
  cursor: pointer;
}

.remember-option input {
  width: 15px;
  height: 15px;
  margin: 0;
  accent-color: var(--login-primary);
}

.login-submit {
  height: 44px;
  font-size: 15px;
  font-weight: 600;
  border-radius: 12px;
  background: var(--login-primary) !important;
}

.login-submit:hover {
  background: var(--login-primary-dark) !important;
}

/* ===== Naive UI 组件样式覆盖 ===== */
.login-card :deep(.n-form-item-label) {
  color: var(--login-text);
  font-size: 13px;
  font-weight: 600;
}

.login-card :deep(.n-form-item) {
  margin-bottom: 12px;
}

.login-card :deep(.n-input),
.login-card :deep(.n-input--focus) {
  min-height: 42px;
  border-radius: 8px;
  background-color: var(--login-input-surface);

  --n-color: var(--login-input-surface);
  --n-color-focus: var(--login-input-surface);
  --n-border: 1px solid var(--login-input-border);
  --n-border-hover: 1px solid var(--login-input-border-hover) !important;
  --n-border-focus: 1px solid var(--login-input-border-focus) !important;
  --n-box-shadow-focus: var(--login-input-focus-shadow);
}

.login-card :deep(.n-input__input-el),
.login-card :deep(.n-input__textarea-el) {
  color: var(--login-text);
}

.login-card :deep(.n-input__placeholder) {
  color: var(--login-muted);
}

.login-card :deep(.n-button--primary-type) {
  --n-color: var(--login-primary);
  --n-color-hover: var(--login-primary-dark);
  --n-color-pressed: var(--login-primary-dark);
  --n-border: 1px solid var(--login-primary);
  --n-border-hover: 1px solid var(--login-primary-dark) !important;
  --n-border-pressed: 1px solid var(--login-primary-dark) !important;
}

/* ===== 深色模式 ===== */
.login-page--dark {
  --login-bg: #1b2220;
  --login-surface: #252e2b;
  --login-input-surface: #3c3c3e;
  --login-text: #eef5f1;
  --login-muted: #a2b0aa;
  --login-primary: #7c89db;
  --login-primary-dark: #6976c8;
  --login-accent: #aeb8f3;
  --login-input-border: #5f6a8f;
  --login-input-border-hover: #7c89db;
  --login-input-border-focus: #7c89db;
  --login-input-focus-shadow: 0 0 0 2px rgb(124 137 219 / 24%);
  --login-card-shadow: 0 4px 41px 13px rgb(0 0 0 / 30%);
  --login-gradient-start: rgb(11 17 50 / 12%);
  --login-gradient-end: rgb(10 15 43 / 42%);
}

.login-page--dark .login-brand-panel {
  background: linear-gradient(135deg, #343d78 0%, #4a558e 50%, #303867 100%);
}

.login-page--dark .brand-logo {
  color: #626fc2;
  border: 1px solid rgb(174 184 243 / 45%);
  background: #eef1ff;
  box-shadow: 0 4px 12px rgb(11 17 50 / 30%);
}

.login-page--dark .brand-decoration {
  opacity: 0.36;
}

.login-page--dark .brand-illustration-svg {
  filter: drop-shadow(0 8px 24px rgb(7 11 34 / 34%));
}

.login-page--dark .login-workspace {
  background: linear-gradient(135deg, #20252e 0%, #1e232d 52%, #1a1f29 100%);
}

.login-page--dark .login-card {
  background: var(--login-surface);
}

.login-page--dark .login-title {
  color: var(--login-accent);
}

/* ===== 响应式 ===== */
@media (width <= 900px) {
  .login-page {
    grid-template-columns: minmax(0, 1.7fr) minmax(390px, 1fr);
  }

  .login-brand-panel {
    padding-right: 40px;
    padding-left: 40px;
  }

  .login-workspace {
    padding-right: 20px;
    padding-left: 20px;
  }

  .brand-illustration-svg {
    width: min(100%, 500px);
  }
}

@media (width <= 760px) {
  .login-page {
    grid-template-columns: minmax(0, 1fr);
    grid-template-rows: 150px minmax(0, 1fr);
  }

  .login-brand-panel {
    min-height: 0;
    padding: 20px 24px 18px;
  }

  .brand-illustration {
    display: none;
  }

  .brand-decoration--top {
    display: none;
  }

  .brand-title {
    font-size: 22px;
  }

  .brand-subtitle {
    margin-top: 6px;
    font-size: 13px;
  }

  .login-workspace {
    min-height: 0;
    padding: 18px 24px 24px;
  }

  .login-card {
    width: 100%;
    min-width: 0;
    max-height: calc(100dvh - 168px);
    padding: 24px 24px 20px;
  }
}

@media (width <= 420px) {
  .login-brand-panel {
    padding-right: 16px;
    padding-left: 16px;
  }

  .brand-title {
    font-size: 24px;
  }

  .login-workspace {
    padding: 16px;
  }

  .login-card {
    padding: 20px 18px 16px;
  }

  .captcha-field {
    grid-template-columns: minmax(0, 1fr) 104px;
  }
}
</style>
