<script setup lang="ts">
import { computed } from 'vue'
import { CheckmarkDoneOutline } from '@vicons/ionicons5'
import { NButton, NIcon, NModal } from 'naive-ui'
import type { FormItemRule } from 'naive-ui'

import AppForm from '@/components/AppForm/index.vue'
import { useLocale } from '@/hooks'
import type { AppFormField, DepartmentFormModalProps, DepartmentFormModel } from '@/types'
import { createDepartmentParentOptions } from '../options'

defineOptions({ name: 'DepartmentFormModal' })

const props = defineProps<DepartmentFormModalProps>()
const emit = defineEmits<{
  'update:show': [value: boolean]
  submit: [model: DepartmentFormModel]
  reset: []
}>()

const { t } = useLocale()

const statusOptions = computed(() => [
  { label: t('department.status.enabled'), value: '1' as const },
  { label: t('department.status.disabled'), value: '0' as const },
])

const parentOptions = computed(() =>
  createDepartmentParentOptions(props.departments, props.editingId, t('department.form.root')),
)

const requiredNameRule: FormItemRule = {
  required: true,
  validator: (_rule, value: unknown) =>
    typeof value === 'string' && value.trim().length > 0
      ? true
      : new Error(t('department.form.namePlaceholder')),
  trigger: ['input', 'blur'],
}

const parentRule: FormItemRule = {
  required: true,
  validator: (_rule, value: unknown) =>
    typeof value === 'number' && value >= 0
      ? true
      : new Error(t('department.form.parentPlaceholder')),
  trigger: ['change'],
}

const orderRule: FormItemRule = {
  required: true,
  validator: (_rule, value: unknown) =>
    typeof value === 'number' && Number.isInteger(value)
      ? true
      : new Error(t('department.form.sortPlaceholder')),
  trigger: ['input', 'blur'],
}

const fields = computed<ReadonlyArray<AppFormField<DepartmentFormModel>>>(() => [
  {
    key: 'parent_id',
    path: 'parent_id',
    label: t('department.form.parent'),
    type: 'tree-select',
    required: true,
    rules: parentRule,
    componentProps: {
      clearable: false,
      defaultExpandAll: true,
      filterable: true,
      options: parentOptions.value,
      placeholder: t('department.form.parentPlaceholder'),
    },
    valueTransform: (value: unknown) => (typeof value === 'number' ? value : Number(value) || 0),
  },
  {
    key: 'dept_name',
    path: 'dept_name',
    label: t('department.form.name'),
    required: true,
    rules: requiredNameRule,
    componentProps: {
      clearable: true,
      maxlength: 50,
      showCount: true,
      placeholder: t('department.form.namePlaceholder'),
    },
  },
  {
    key: 'order_num',
    path: 'order_num',
    label: t('department.form.sort'),
    type: 'number',
    required: true,
    rules: orderRule,
    componentProps: {
      precision: 0,
      placeholder: t('department.form.sortPlaceholder'),
    },
  },
  {
    key: 'leader',
    path: 'leader',
    label: t('department.form.leader'),
    componentProps: {
      clearable: true,
      maxlength: 50,
      placeholder: t('department.form.leaderPlaceholder'),
    },
  },
  {
    key: 'phone',
    path: 'phone',
    label: t('department.form.phone'),
    componentProps: {
      clearable: true,
      maxlength: 20,
      placeholder: t('department.form.phonePlaceholder'),
    },
  },
  {
    key: 'email',
    path: 'email',
    label: t('department.form.email'),
    componentProps: {
      clearable: true,
      maxlength: 100,
      placeholder: t('department.form.emailPlaceholder'),
    },
  },
  {
    key: 'status',
    path: 'status',
    label: t('department.form.status'),
    type: 'select',
    required: true,
    componentProps: {
      options: statusOptions.value,
      placeholder: t('department.form.statusPlaceholder'),
    },
  },
])

const handleShowUpdate = (value: boolean): void => emit('update:show', value)
const handleCancel = (): void => emit('update:show', false)
const handleSubmit = (model: DepartmentFormModel): void => emit('submit', model)
</script>

<template>
  <NModal
    :show="props.show"
    preset="card"
    class="department-modal"
    :title="props.mode === 'create' ? t('department.createTitle') : t('department.editTitle')"
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
          {{ t('department.form.cancel') }}
        </NButton>
        <NButton
          v-permission="props.mode === 'create' ? 'system:dept:add' : 'system:dept:edit'"
          attr-type="button"
          type="primary"
          :loading="actionLoading"
          :disabled="actionLoading"
          @click="submit"
        >
          <template #icon>
            <NIcon><CheckmarkDoneOutline /></NIcon>
          </template>
          {{ t('department.form.save') }}
        </NButton>
      </template>
    </AppForm>
  </NModal>
</template>

<style lang="scss">
.n-card.department-modal {
  width: min(760px, calc(100vw - 32px));
}
</style>
