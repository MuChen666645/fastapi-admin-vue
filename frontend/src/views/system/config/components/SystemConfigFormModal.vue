<script setup lang="ts">
import { computed } from 'vue'
import { CheckmarkDoneOutline } from '@vicons/ionicons5'
import { NButton, NIcon, NModal } from 'naive-ui'
import type { FormItemRule } from 'naive-ui'

import AppForm from '@/components/AppForm/index.vue'
import { useLocale } from '@/hooks'
import type { AppFormField, SystemConfigFormModalProps, SystemConfigFormModel } from '@/types'

defineOptions({ name: 'SystemConfigFormModal' })

const props = defineProps<SystemConfigFormModalProps>()
const emit = defineEmits<{
  'update:show': [value: boolean]
  submit: [model: SystemConfigFormModel]
  reset: []
}>()

const { t } = useLocale()

const requiredTextRule = (message: string): FormItemRule => ({
  required: true,
  validator: (_rule, value: unknown) =>
    typeof value === 'string' && value.trim().length > 0 ? true : new Error(message),
  trigger: ['input', 'blur'],
})

const configKeyRule = computed<FormItemRule>(() => ({
  required: true,
  validator: (_rule, value: unknown) =>
    typeof value === 'string' && /^[A-Za-z][A-Za-z0-9_.:-]*$/.test(value.trim())
      ? true
      : new Error(t('systemConfig.form.keyInvalid')),
  trigger: ['input', 'blur'],
}))

const fields = computed<ReadonlyArray<AppFormField<SystemConfigFormModel>>>(() => [
  {
    key: 'config_name',
    path: 'config_name',
    label: t('systemConfig.form.name'),
    required: true,
    rules: requiredTextRule(t('systemConfig.form.namePlaceholder')),
    componentProps: {
      clearable: true,
      maxlength: 100,
      showCount: true,
      placeholder: t('systemConfig.form.namePlaceholder'),
    },
  },
  {
    key: 'config_key',
    path: 'config_key',
    label: t('systemConfig.form.key'),
    required: true,
    disabled: () => props.mode === 'edit',
    rules: configKeyRule.value,
    componentProps: {
      clearable: true,
      maxlength: 100,
      showCount: true,
      placeholder: t('systemConfig.form.keyPlaceholder'),
    },
  },
  {
    key: 'config_type',
    path: 'config_type',
    label: t('systemConfig.form.type'),
    required: true,
    rules: requiredTextRule(t('systemConfig.form.typePlaceholder')),
    componentProps: {
      clearable: true,
      maxlength: 20,
      showCount: true,
      placeholder: t('systemConfig.form.typePlaceholder'),
    },
  },
  {
    key: 'is_builtin',
    path: 'is_builtin',
    label: t('systemConfig.form.builtin'),
    type: 'switch',
    hidden: () => props.mode === 'edit',
  },
  {
    key: 'config_value',
    path: 'config_value',
    label: t('systemConfig.form.value'),
    type: 'textarea',
    componentProps: {
      clearable: true,
      rows: 4,
      placeholder: t('systemConfig.form.valuePlaceholder'),
    },
    span: '1 s:2',
  },
  {
    key: 'remark',
    path: 'remark',
    label: t('systemConfig.form.remark'),
    type: 'textarea',
    componentProps: {
      clearable: true,
      maxlength: 500,
      showCount: true,
      rows: 3,
      placeholder: t('systemConfig.form.remarkPlaceholder'),
    },
    span: '1 s:2',
  },
])

const handleShowUpdate = (value: boolean): void => emit('update:show', value)
const handleCancel = (): void => emit('update:show', false)
const handleSubmit = (model: SystemConfigFormModel): void => emit('submit', model)
</script>

<template>
  <NModal
    :show="props.show"
    preset="card"
    class="system-config-modal"
    :title="props.mode === 'create' ? t('systemConfig.createTitle') : t('systemConfig.editTitle')"
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
          {{ t('systemConfig.form.cancel') }}
        </NButton>
        <NButton
          v-permission="props.mode === 'create' ? 'system:config:add' : 'system:config:edit'"
          attr-type="button"
          type="primary"
          :loading="actionLoading"
          :disabled="actionLoading"
          @click="submit"
        >
          <template #icon>
            <NIcon><CheckmarkDoneOutline /></NIcon>
          </template>
          {{ t('systemConfig.form.save') }}
        </NButton>
      </template>
    </AppForm>
  </NModal>
</template>

<style lang="scss">
.n-card.system-config-modal {
  width: min(760px, calc(100vw - 32px));
}
</style>
