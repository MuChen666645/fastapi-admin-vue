<script setup lang="ts">
import { computed } from 'vue'
import { CheckmarkDoneOutline } from '@vicons/ionicons5'
import { NButton, NIcon, NModal } from 'naive-ui'
import type { FormItemRule } from 'naive-ui'

import AppForm from '@/components/AppForm/index.vue'
import { useLocale } from '@/hooks'
import type { AppFormField, TenantFormModalProps, TenantFormModel } from '@/types'

defineOptions({ name: 'TenantFormModal' })

const props = defineProps<TenantFormModalProps>()
const emit = defineEmits<{
  'update:show': [value: boolean]
  submit: [model: TenantFormModel]
  reset: []
}>()
const { t } = useLocale()

const createRequiredTextRule = (message: string): FormItemRule => ({
  required: true,
  validator: (_rule, value: unknown) =>
    typeof value === 'string' && value.trim().length > 0 ? true : new Error(message),
  trigger: ['input', 'blur'],
})

const codeRule = computed<FormItemRule>(() => ({
  required: true,
  validator: (_rule, value: unknown) =>
    typeof value === 'string' && value.trim().length > 0 && value.trim().length <= 64
      ? true
      : new Error(t('tenant.form.codeInvalid')),
  trigger: ['input', 'blur'],
}))

const statusOptions = computed(() => [
  { label: t('tenant.status.enabled'), value: '1' as const },
  { label: t('tenant.status.disabled'), value: '0' as const },
])

const fields = computed<ReadonlyArray<AppFormField<TenantFormModel>>>(() => [
  {
    key: 'code',
    path: 'code',
    label: t('tenant.form.code'),
    required: true,
    disabled: () => props.mode === 'edit',
    rules: codeRule.value,
    componentProps: {
      clearable: true,
      maxlength: 64,
      showCount: true,
      placeholder: t('tenant.form.codePlaceholder'),
    },
  },
  {
    key: 'name',
    path: 'name',
    label: t('tenant.form.name'),
    required: true,
    rules: createRequiredTextRule(t('tenant.form.namePlaceholder')),
    componentProps: {
      clearable: true,
      maxlength: 100,
      showCount: true,
      placeholder: t('tenant.form.namePlaceholder'),
    },
  },
  {
    key: 'status',
    path: 'status',
    label: t('tenant.form.status'),
    type: 'select',
    required: true,
    hidden: () => props.mode === 'create',
    componentProps: {
      options: statusOptions.value,
      placeholder: t('tenant.form.statusPlaceholder'),
    },
  },
  {
    key: 'description',
    path: 'description',
    label: t('tenant.form.description'),
    type: 'textarea',
    componentProps: {
      clearable: true,
      maxlength: 500,
      showCount: true,
      rows: 4,
      placeholder: t('tenant.form.descriptionPlaceholder'),
    },
    span: '1 s:2',
  },
])

const handleShowUpdate = (value: boolean): void => emit('update:show', value)
const handleCancel = (): void => emit('update:show', false)
const handleSubmit = (model: TenantFormModel): void => emit('submit', model)
</script>

<template>
  <NModal
    :show="props.show"
    preset="card"
    class="tenant-form-modal"
    :title="props.mode === 'create' ? t('tenant.createTitle') : t('tenant.editTitle')"
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
          {{ t('tenant.form.cancel') }}
        </NButton>
        <NButton
          v-permission="props.mode === 'create' ? 'system:tenant:add' : 'system:tenant:edit'"
          attr-type="button"
          type="primary"
          :loading="actionLoading"
          :disabled="actionLoading"
          @click="submit"
        >
          <template #icon>
            <NIcon><CheckmarkDoneOutline /></NIcon>
          </template>
          {{ t('tenant.form.save') }}
        </NButton>
      </template>
    </AppForm>
  </NModal>
</template>

<style lang="scss">
.n-card.tenant-form-modal {
  width: min(720px, calc(100vw - 32px));
}
</style>
