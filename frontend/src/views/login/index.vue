<script setup lang="ts">
import { onMounted, ref } from 'vue'
import {
  NAlert,
  NButton,
  NForm,
  NFormItem,
  NInput,
  NRadioButton,
  NRadioGroup,
  NText,
} from 'naive-ui'
import type { FormInst, FormRules } from 'naive-ui'
import { useRoute, useRouter } from 'vue-router'

import { fetchCaptcha } from '@/api/auth'
import { useTheme } from '@/composables/useTheme'
import { useAuthStore } from '@/stores/auth'
import type { LoginCredentials } from '@/types/api'
import { ApiError } from '@/utils/request'

defineOptions({ name: 'LoginView' })

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const formRef = ref<FormInst | null>(null)
const form = ref({
  loginType: 'username' as LoginCredentials['loginType'],
  identifier: auth.rememberedUsername,
  password: '',
  captcha: '',
  mfaCode: '',
  remember: Boolean(auth.rememberedUsername),
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
        loginType: form.value.loginType,
        identifier: form.value.identifier,
        password: form.value.password,
        captcha_id: captchaId.value,
        captcha: form.value.captcha,
        mfa_code: form.value.mfaCode || undefined,
      },
      form.value.remember,
    )
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
    <section class="login-brand-panel" aria-labelledby="brand-title">
      <div class="brand-header">
        <NText class="brand-name" strong>FastApi管理后台</NText>
      </div>

      <div class="brand-copy">
        <div class="brand-icon" aria-hidden="true">✓</div>
        <NText id="brand-title" tag="h1" class="brand-title" strong>
          高效管理您的业务<br />一切尽在掌控
        </NText>
        <NText class="brand-description">
          完整的后台管理解决方案，实时数据分析、用户管理、订单追踪，一站式搞定。
        </NText>
        <ul class="brand-features" aria-label="系统特性">
          <li><span aria-hidden="true">✓</span>基于角色的权限控制</li>
          <li><span aria-hidden="true">✓</span>实时数据分析仪表盘</li>
          <li><span aria-hidden="true">✓</span>完整的操作审计日志</li>
        </ul>
      </div>

      <NText class="brand-copyright">© 2026 管理后台，保留所有权利。</NText>
    </section>

    <section class="login-workspace" aria-labelledby="login-title">
      <button
        type="button"
        class="theme-toggle"
        :aria-label="isDarkMode ? '切换浅色主题' : '切换深色主题'"
        :title="isDarkMode ? '切换浅色主题' : '切换深色主题'"
        @click="toggleTheme"
      >
        <span aria-hidden="true">{{ isDarkMode ? '☀' : '☾' }}</span>
      </button>

      <div class="login-form-shell">
        <div class="login-heading">
          <NText id="login-title" tag="h2" class="login-title" strong>欢迎回来</NText>
          <NText class="login-subtitle">登录您的管理后台账号</NText>
        </div>

        <NAlert v-if="errorMessage" type="error" :show-icon="false" class="login-error">
          {{ errorMessage }}
        </NAlert>

        <NForm ref="formRef" :model="form" :rules="rules" label-placement="top" size="large">
          <NFormItem label="登录方式" path="loginType">
            <NRadioGroup v-model:value="form.loginType" name="loginType" class="login-method">
              <NRadioButton value="username">用户名</NRadioButton>
              <NRadioButton value="phone">手机号</NRadioButton>
            </NRadioGroup>
          </NFormItem>

          <NFormItem :label="form.loginType === 'username' ? '用户名' : '手机号'" path="identifier">
            <NInput
              v-model:value="form.identifier"
              :placeholder="form.loginType === 'username' ? '请输入用户名' : '请输入手机号'"
              autocomplete="username"
            />
          </NFormItem>

          <NFormItem label="密码" path="password">
            <NInput
              v-model:value="form.password"
              type="password"
              placeholder="请输入密码"
              show-password-on="click"
              autocomplete="current-password"
            />
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
                <span v-else>{{ captchaLoading ? '加载中' : '点击刷新' }}</span>
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
              <span>记住登录名</span>
            </label>
            <NText class="login-help">验证码每次登录必填</NText>
          </div>

          <NButton
            type="primary"
            block
            class="login-submit"
            :loading="submitting"
            @click="handleLogin"
          >
            立即登录
          </NButton>
        </NForm>

        <div class="login-security-note">
          <span class="security-dot" aria-hidden="true"></span>
          <span>登录后将根据服务端权限加载可访问菜单</span>
        </div>
      </div>
    </section>
  </main>
</template>

<style scoped>
.login-page {
  --login-background: #f1f3f6;
  --login-surface: #fff;
  --login-text: #17211f;
  --login-muted: #87918f;
  --login-border: #dde3e5;
  --login-primary: #18a357;
  --login-primary-dark: #0f8a49;

  display: grid;
  min-height: 100vh;
  color: var(--login-text);
  background: var(--login-background);
  grid-template-columns: minmax(360px, 60vw) minmax(0, 1fr);
}

.login-page--dark {
  --login-background: #1a211f;
  --login-surface: #232c29;
  --login-text: #f3f7f5;
  --login-muted: #a5b1ac;
  --login-border: #3c4a45;
}

.login-brand-panel {
  position: relative;
  display: flex;
  min-height: 100vh;
  flex-direction: column;
  overflow: hidden;
  padding: 42px 36px 30px;
  color: #fff;
  background: var(--login-primary);
  isolation: isolate;
}

.login-brand-panel::before,
.login-brand-panel::after {
  position: absolute;
  z-index: -1;
  border: 1px solid rgb(255 255 255 / 16%);
  border-radius: 50%;
  content: '';
  pointer-events: none;
}

.login-brand-panel::before {
  top: -170px;
  left: -220px;
  width: 660px;
  height: 660px;
  box-shadow:
    0 0 0 52px rgb(255 255 255 / 7%),
    0 0 0 104px rgb(255 255 255 / 6%),
    0 0 0 156px rgb(255 255 255 / 5%),
    0 0 0 208px rgb(255 255 255 / 4%);
}

.login-brand-panel::after {
  right: -170px;
  bottom: -270px;
  width: 470px;
  height: 470px;
  border-color: rgb(255 255 255 / 11%);
}

.brand-header,
.brand-copy,
.brand-copyright {
  position: relative;
  z-index: 1;
}

.brand-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.brand-mark {
  display: grid;
  width: 28px;
  height: 28px;
  place-items: center;
  border: 1px solid rgb(255 255 255 / 28%);
  border-radius: 6px;
  background: rgb(255 255 255 / 15%);
  font-size: 13px;
  font-weight: 700;
}

.brand-name {
  color: #fff;
  font-size: 15px;
}

.brand-copy {
  max-width: 440px;
  margin-top: auto;
  margin-bottom: auto;
}

.brand-icon {
  display: grid;
  width: 48px;
  height: 48px;
  margin-bottom: 22px;
  place-items: center;
  border: 1px solid rgb(255 255 255 / 22%);
  border-radius: 13px;
  background: rgb(255 255 255 / 13%);
  font-size: 30px;
  font-weight: 300;
  line-height: 1;
}

.brand-title {
  margin: 0;
  color: #fff;
  font-size: clamp(28px, 2.6vw, 37px);
  line-height: 1.3;
}

.brand-description {
  display: block;
  max-width: 410px;
  margin-top: 18px;
  color: rgb(255 255 255 / 82%);
  font-size: 13px;
  line-height: 1.8;
}

.brand-features {
  display: grid;
  gap: 13px;
  margin: 26px 0 0;
  padding: 0;
  color: rgb(255 255 255 / 92%);
  font-size: 13px;
  list-style: none;
}

.brand-features li {
  display: flex;
  align-items: center;
  gap: 10px;
}

.brand-features li span {
  display: grid;
  width: 16px;
  height: 16px;
  place-items: center;
  border: 1px solid rgb(255 255 255 / 72%);
  border-radius: 50%;
  font-size: 11px;
}

.brand-copyright {
  color: rgb(255 255 255 / 62%);
  font-size: 11px;
}

.login-workspace {
  position: relative;
  display: grid;
  min-height: 100vh;
  place-items: center;
  padding: 76px 40px 52px;
}

.theme-toggle {
  position: absolute;
  top: 26px;
  right: 28px;
  display: grid;
  width: 32px;
  height: 32px;
  padding: 0;
  place-items: center;
  color: var(--login-muted);
  border: 0;
  border-radius: 50%;
  background: transparent;
  cursor: pointer;
  font-size: 19px;
  line-height: 1;
}

.theme-toggle:hover,
.theme-toggle:focus-visible {
  color: var(--login-primary);
  background: rgb(24 163 87 / 10%);
  outline: none;
}

.login-form-shell {
  width: min(100%, 360px);
}

.login-heading {
  display: grid;
  gap: 7px;
  margin-bottom: 25px;
}

.login-title {
  margin: 0;
  color: var(--login-text);
  font-size: 26px;
  line-height: 1.25;
}

.login-subtitle,
.login-help,
.login-security-note {
  color: var(--login-muted);
}

.login-subtitle {
  font-size: 13px;
}

.login-error {
  margin-bottom: 18px;
}

.login-method {
  display: flex;
  width: 100%;
}

.login-method :deep(.n-radio-button) {
  flex: 1;
}

.login-method :deep(.n-radio-button__label) {
  width: 100%;
  text-align: center;
}

.captcha-field {
  display: grid;
  width: 100%;
  grid-template-columns: minmax(0, 1fr) 112px;
  gap: 9px;
}

.captcha-image {
  display: grid;
  min-width: 0;
  height: 40px;
  padding: 0;
  place-items: center;
  overflow: hidden;
  color: var(--login-muted);
  border: 1px solid var(--login-border);
  border-radius: 4px;
  background: var(--login-surface);
  cursor: pointer;
  font-size: 12px;
}

.captcha-image:hover:not(:disabled),
.captcha-image:focus-visible {
  border-color: var(--login-primary);
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
  justify-content: space-between;
  gap: 12px;
  margin: 1px 0 19px;
}

.remember-option {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: var(--login-muted);
  font-size: 12px;
  cursor: pointer;
}

.remember-option input {
  width: 14px;
  height: 14px;
  margin: 0;
  accent-color: var(--login-primary);
}

.login-help {
  font-size: 12px;
  text-align: right;
}

.login-submit {
  height: 42px;
  font-size: 14px;
  font-weight: 600;
}

.login-submit :deep(.n-button__content) {
  letter-spacing: 0;
}

.login-security-note {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  margin-top: 21px;
  font-size: 11px;
  text-align: center;
}

.security-dot {
  width: 6px;
  height: 6px;
  flex: 0 0 auto;
  border-radius: 50%;
  background: var(--login-primary);
}

.login-form-shell :deep(.n-form-item-label) {
  color: var(--login-text);
  font-size: 12px;
  font-weight: 600;
}

.login-form-shell :deep(.n-form-item) {
  margin-bottom: 17px;
}

.login-form-shell :deep(.n-input),
.login-form-shell :deep(.n-radio-button) {
  border-color: var(--login-border);
  background: var(--login-surface);
}

.login-form-shell :deep(.n-input) {
  --n-border: 1px solid var(--login-border);
  --n-border-hover: 1px solid var(--login-primary);
  --n-border-focus: 1px solid var(--login-primary);
  --n-box-shadow-focus: 0 0 0 2px rgb(24 163 87 / 12%);
}

.login-form-shell :deep(.n-input__input-el),
.login-form-shell :deep(.n-input__placeholder) {
  color: var(--login-text);
}

.login-form-shell :deep(.n-input__placeholder) {
  color: var(--login-muted);
}

.login-form-shell :deep(.n-radio-button--checked) {
  color: var(--login-primary-dark);
  border-color: var(--login-primary);
  background: rgb(24 163 87 / 9%);
}

.login-form-shell :deep(.n-button--primary-type) {
  --n-color: var(--login-primary);
  --n-color-hover: var(--login-primary-dark);
  --n-color-pressed: var(--login-primary-dark);
  --n-border: 1px solid var(--login-primary);
  --n-border-hover: 1px solid var(--login-primary-dark);
  --n-border-pressed: 1px solid var(--login-primary-dark);
}

@media (width <= 760px) {
  .login-page {
    grid-template-columns: 1fr;
  }

  .login-brand-panel {
    min-height: 390px;
    padding: 28px 24px 24px;
  }

  .brand-copy {
    margin-top: 54px;
    margin-bottom: 38px;
  }

  .brand-title {
    font-size: 30px;
  }

  .login-workspace {
    min-height: auto;
    padding: 54px 22px 44px;
  }
}

@media (width <= 420px) {
  .login-brand-panel {
    min-height: 360px;
  }

  .brand-description {
    font-size: 12px;
  }

  .login-workspace {
    padding-right: 16px;
    padding-left: 16px;
  }

  .captcha-field {
    grid-template-columns: minmax(0, 1fr) 100px;
  }
}
</style>
