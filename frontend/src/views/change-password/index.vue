<script setup lang="ts">
import { ref } from 'vue'
import { NAlert, NButton, NCard, NForm, NFormItem, NInput, NText } from 'naive-ui'
import type { FormInst, FormRules } from 'naive-ui'
import { useRouter } from 'vue-router'

import { useAuthStore } from '@/stores/auth'

defineOptions({ name: 'ChangePasswordView' })

const router = useRouter()
const auth = useAuthStore()
const formRef = ref<FormInst | null>(null)
const form = ref({ oldPassword: '', newPassword: '', confirmPassword: '' })
const errorMessage = ref('')
const submitting = ref(false)

const rules: FormRules = {
  oldPassword: { required: true, message: '请输入当前密码', trigger: ['input', 'blur'] },
  newPassword: {
    required: true,
    min: 8,
    message: '新密码至少需要 8 位',
    trigger: ['input', 'blur'],
  },
  confirmPassword: {
    required: true,
    validator: (_rule, value: string) => value === form.value.newPassword,
    message: '两次输入的新密码不一致',
    trigger: ['input', 'blur'],
  },
}

const handleSubmit = async (): Promise<void> => {
  if (!formRef.value || submitting.value) {
    return
  }

  try {
    await formRef.value.validate()
  } catch {
    return
  }

  submitting.value = true
  errorMessage.value = ''
  try {
    await auth.updatePassword(form.value.oldPassword, form.value.newPassword)
    await router.replace({ path: '/' })
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '密码修改失败，请稍后重试'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <main class="password-page grid min-h-screen">
    <NCard bordered class="password-card">
      <div class="password-heading">
        <NText class="password-kicker">安全设置</NText>
        <NText tag="h1" class="password-title" strong>请先修改密码</NText>
        <NText depth="3">当前账号需要完成密码更新后才能进入管理工作台。</NText>
      </div>
      <NAlert v-if="errorMessage" type="error" :show-icon="false" class="password-error">
        {{ errorMessage }}
      </NAlert>
      <NForm ref="formRef" :model="form" :rules="rules" label-placement="top" size="large">
        <NFormItem label="当前密码" path="oldPassword">
          <NInput v-model:value="form.oldPassword" type="password" show-password-on="click" />
        </NFormItem>
        <NFormItem label="新密码" path="newPassword">
          <NInput v-model:value="form.newPassword" type="password" show-password-on="click" />
        </NFormItem>
        <NFormItem label="确认新密码" path="confirmPassword">
          <NInput v-model:value="form.confirmPassword" type="password" show-password-on="click" />
        </NFormItem>
        <NButton type="primary" block :loading="submitting" @click="handleSubmit">
          更新密码
        </NButton>
      </NForm>
    </NCard>
  </main>
</template>

<style scoped>
.password-page {
  place-items: center;
  padding: 24px;
  background: var(--app-color-page);
}

.password-card {
  width: min(100%, 460px);
  border-radius: 10px;
}

.password-heading {
  display: grid;
  gap: 8px;
  margin-bottom: 28px;
}

.password-kicker {
  color: var(--app-color-primary);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.password-title {
  margin: 0;
  font-size: 28px;
}

.password-error {
  margin-bottom: 18px;
}
</style>
