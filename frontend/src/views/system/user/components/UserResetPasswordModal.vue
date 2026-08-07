<script setup lang="ts">
import { computed } from 'vue'

import { CheckmarkDoneOutline } from '@vicons/ionicons5'
import { NButton, NIcon, NModal } from 'naive-ui'
import type { FormItemRule } from 'naive-ui'

import AppForm from '@/components/AppForm/index.vue'
import { useLocale } from '@/hooks'
import type { AppFormField, UserResetPasswordModel } from '@/types'

defineOptions({ name: 'UserResetPasswordModal' })

interface UserResetPasswordModalProps {
  show: boolean
  model: UserResetPasswordModel
  loading: boolean
}

const props = defineProps<UserResetPasswordModalProps>()

const emit = defineEmits<{
  'update:show': [value: boolean]
  submit: [model: UserResetPasswordModel]
  reset: []
}>()

const { t } = useLocale()

const validatePassword = (_rule: FormItemRule, value: unknown): boolean | Error => {
  if (typeof value !== 'string' || value.trim().length === 0) {
    return new Error(t('user.form.passwordPlaceholder'))
  }

  return value.length >= 8 ? true : new Error(t('user.form.passwordTooShort'))
}

const fields = computed<ReadonlyArray<AppFormField<UserResetPasswordModel>>>(() => [
  {
    key: 'password',
    path: 'password',
    label: t('user.form.password'),
    type: 'password',
    required: true,
    requiredMessage: t('user.form.passwordPlaceholder'),
    rules: [{ required: true, validator: validatePassword, trigger: ['input', 'blur'] }],
  },
])

const handleCancel = (): void => emit('update:show', false)
</script>

<template>
  <NModal
    :show="props.show"
    preset="card"
    class="user-password-modal"
    :title="t('user.resetPasswordTitle')"
    :mask-closable="false"
    @update:show="emit('update:show', $event)"
    @after-leave="emit('reset')"
  >
    <AppForm
      :model="props.model"
      :fields="fields"
      :loading="props.loading"
      :show-reset="false"
      @submit="emit('submit', $event)"
    >
      <template #actions="{ loading: actionLoading, submit }">
        <NButton attr-type="button" :disabled="actionLoading" @click="handleCancel">
          {{ t('user.form.cancel') }}
        </NButton>
        <NButton
          v-permission="'system:user:resetPwd'"
          attr-type="button"
          type="primary"
          :loading="actionLoading"
          :disabled="actionLoading"
          @click="submit"
        >
          <template #icon>
            <NIcon><CheckmarkDoneOutline /></NIcon>
          </template>
          {{ t('user.form.save') }}
        </NButton>
      </template>
    </AppForm>
  </NModal>
</template>

<style lang="scss">
.n-card.user-password-modal {
  width: min(460px, calc(100vw - 32px));
}
</style>
