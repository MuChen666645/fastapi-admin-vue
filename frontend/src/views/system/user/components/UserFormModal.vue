<script setup lang="ts">
import { computed } from 'vue'
import { CheckmarkDoneOutline } from '@vicons/ionicons5'
import { NButton, NIcon, NModal } from 'naive-ui'
import type { FormItemRule } from 'naive-ui'

import AppForm from '@/components/AppForm/index.vue'
import { useLocale } from '@/hooks'
import {
  getPasswordValidationMessageKey,
  toUserSexSelectOptions,
  validateEmail,
  validatePassword,
  validatePhone,
} from '@/utils'
import type {
  AppFormField,
  DepartmentCascaderOption,
  DepartmentOption,
  UserFormModalProps,
  UserFormModel,
} from '@/types'

defineOptions({ name: 'UserFormModal' })

const props = defineProps<UserFormModalProps>()

const emit = defineEmits<{
  'update:show': [value: boolean]
  submit: [model: UserFormModel]
  reset: []
}>()

const { t } = useLocale()

const toCascaderOptions = (departments: DepartmentOption[]): DepartmentCascaderOption[] =>
  departments.map((department) => {
    const children = toCascaderOptions(department.children)
    return {
      label: department.dept_name,
      value: department.dept_id,
      disabled: department.status !== '1',
      ...(children.length > 0 ? { children } : {}),
    }
  })

const departmentOptions = computed(() => toCascaderOptions(props.departments))
const postOptions = computed(() =>
  props.posts.map((post) => ({
    label: post.post_name,
    value: post.post_id,
    disabled: post.status !== '1',
  })),
)
const roleOptions = computed(() =>
  props.roles
    .filter((role) => role.code.trim().toLowerCase() !== 'admin')
    .map((role) => ({
      label: role.name,
      value: role.id,
      disabled: role.status !== '1',
    })),
)

const validatePhoneField = (_rule: FormItemRule, value: unknown): boolean | Error => {
  if (typeof value !== 'string' || value.trim().length === 0) {
    return props.mode === 'create' ? new Error(t('user.form.phonePlaceholder')) : true
  }

  return validatePhone(value) ? true : new Error(t('user.form.invalidPhone'))
}

const validateEmailField = (_rule: FormItemRule, value: unknown): boolean | Error => {
  if (typeof value !== 'string' || value.trim().length === 0) {
    return true
  }

  return validateEmail(value) ? true : new Error(t('user.form.invalidEmail'))
}

const validatePasswordField = (_rule: FormItemRule, value: unknown): boolean | Error => {
  const result = validatePassword(value, props.model.username)
  return result.valid ? true : new Error(t(getPasswordValidationMessageKey(result.code)))
}

const sexOptions = computed(() => toUserSexSelectOptions(props.sexOptions))

const statusOptions = computed(() => [
  { label: t('user.status.enabled'), value: '1' as const },
  { label: t('user.status.disabled'), value: '0' as const },
])

const fields = computed<ReadonlyArray<AppFormField<UserFormModel>>>(() => [
  {
    key: 'username',
    path: 'username',
    label: t('user.form.username'),
    required: true,
    requiredMessage: t('user.form.usernamePlaceholder'),
    componentProps: { placeholder: t('user.form.usernamePlaceholder') },
  },
  {
    key: 'password',
    path: 'password',
    label: t('user.form.password'),
    type: 'password',
    required: props.mode === 'create',
    hidden: () => props.mode !== 'create',
    rules: [{ validator: validatePasswordField, trigger: ['input', 'blur'] }],
    componentProps: { placeholder: t('user.form.passwordPlaceholder'), showPasswordOn: 'click' },
  },
  {
    key: 'phone',
    path: 'phone',
    label: t('user.form.phone'),
    required: props.mode === 'create',
    rules: [{ validator: validatePhoneField, trigger: ['input', 'blur'] }],
    componentProps: { clearable: true, placeholder: t('user.form.phonePlaceholder') },
  },
  {
    key: 'email',
    path: 'email',
    label: t('user.form.email'),
    rules: [{ validator: validateEmailField, trigger: ['input', 'blur'] }],
    componentProps: { clearable: true, placeholder: t('user.form.emailPlaceholder') },
  },
  {
    key: 'nickname',
    path: 'nickname',
    label: t('user.form.nickname'),
    componentProps: { clearable: true, placeholder: t('user.form.nicknamePlaceholder') },
  },
  {
    key: 'sex',
    path: 'sex',
    label: t('user.form.sex'),
    type: 'select',
    componentProps: {
      clearable: true,
      options: sexOptions.value,
      placeholder: t('user.form.sexPlaceholder'),
    },
  },
  {
    key: 'status',
    path: 'status',
    label: t('user.form.status'),
    type: 'select',
    hidden: () => props.mode !== 'edit',
    componentProps: { options: statusOptions.value, placeholder: t('user.form.statusPlaceholder') },
  },
  {
    key: 'dept_id',
    path: 'dept_id',
    label: t('user.form.department'),
    type: 'cascader',
    componentProps: {
      clearable: true,
      expandTrigger: 'hover',
      filterable: true,
      options: departmentOptions.value,
      placeholder: t('user.form.departmentPlaceholder'),
      showPath: true,
    },
  },
  {
    key: 'post_ids',
    path: 'post_ids',
    label: t('user.form.post'),
    type: 'select',
    componentProps: {
      multiple: true,
      clearable: true,
      options: postOptions.value,
      placeholder: t('user.form.postPlaceholder'),
    },
    span: '1 s:2',
  },
  {
    key: 'role_ids',
    path: 'role_ids',
    label: t('user.form.role'),
    type: 'select',
    componentProps: {
      multiple: true,
      clearable: true,
      options: roleOptions.value,
      placeholder: t('user.form.rolePlaceholder'),
    },
    span: '1 s:2',
  },
])

const handleShowUpdate = (value: boolean): void => emit('update:show', value)
const handleCancel = (): void => emit('update:show', false)
const handleSubmit = (model: UserFormModel): void => emit('submit', model)
</script>

<template>
  <NModal
    :show="props.show"
    preset="card"
    class="user-modal"
    :title="props.mode === 'create' ? t('user.createTitle') : t('user.editTitle')"
    :mask-closable="false"
    @update:show="handleShowUpdate"
    @after-leave="emit('reset')"
  >
    <AppForm
      :model="props.model"
      :fields="fields"
      :loading="props.loading"
      :show-reset="false"
      :layout="{
        labelPlacement: 'top',
        columns: '1 s:2',
        responsive: 'screen',
        xGap: 16,
        yGap: 4,
      }"
      @submit="handleSubmit"
    >
      <template #actions="{ loading: actionLoading, submit }">
        <NButton attr-type="button" :disabled="actionLoading" @click="handleCancel">
          {{ t('user.form.cancel') }}
        </NButton>
        <NButton
          v-permission="props.mode === 'create' ? 'system:user:add' : 'system:user:edit'"
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
.n-card.user-modal {
  width: min(760px, calc(100vw - 32px));
}
</style>
