<script setup lang="ts">
import { computed } from 'vue'
import { CheckmarkDoneOutline } from '@vicons/ionicons5'
import { NButton, NIcon, NModal } from 'naive-ui'
import type { FormItemRule } from 'naive-ui'

import AppForm from '@/components/AppForm/index.vue'
import { useLocale } from '@/hooks'
import type { AppFormField, ScheduledJobFormModalProps, ScheduledJobFormModel } from '@/types'

defineOptions({ name: 'JobFormModal' })

const props = defineProps<ScheduledJobFormModalProps>()
const emit = defineEmits<{
  'update:show': [value: boolean]
  submit: [model: ScheduledJobFormModel]
  reset: []
}>()
const { t } = useLocale()

const createRequiredTextRule = (
  message: string,
  maximumLength: number,
  pattern?: RegExp,
): FormItemRule => ({
  required: true,
  validator: (_rule, value: unknown) => {
    if (typeof value !== 'string') {
      return new Error(message)
    }

    const normalizedValue = value.trim()
    return normalizedValue.length > 0 &&
      normalizedValue.length <= maximumLength &&
      (!pattern || pattern.test(normalizedValue))
      ? true
      : new Error(message)
  },
  trigger: ['input', 'blur'],
})

const createIntegerRule = (message: string, minimum: number, maximum: number): FormItemRule => ({
  required: true,
  validator: (_rule, value: unknown) =>
    typeof value === 'number' && Number.isInteger(value) && value >= minimum && value <= maximum
      ? true
      : new Error(message),
  trigger: ['input', 'blur'],
})

const cronRule = computed<FormItemRule>(() =>
  createRequiredTextRule(t('job.form.cronInvalid'), 100, /^\S+\s+\S+\s+\S+\s+\S+\s+\S+$/),
)

const argumentsRule = computed<FormItemRule>(() => ({
  required: true,
  validator: (_rule, value: unknown) => {
    if (typeof value !== 'string' || value.trim().length === 0 || value.length > 10_000) {
      return new Error(t('job.form.argumentsInvalid'))
    }

    try {
      const parsed: unknown = JSON.parse(value)
      return typeof parsed === 'object' && parsed !== null && !Array.isArray(parsed)
        ? true
        : new Error(t('job.form.argumentsInvalid'))
    } catch {
      return new Error(t('job.form.argumentsInvalid'))
    }
  },
  trigger: ['input', 'blur'],
}))

const statusOptions = computed(() => [
  { label: t('job.status.enabled'), value: '1' as const },
  { label: t('job.status.disabled'), value: '0' as const },
])

const fields = computed<ReadonlyArray<AppFormField<ScheduledJobFormModel>>>(() => [
  {
    key: 'job_name',
    path: 'job_name',
    label: t('job.form.name'),
    required: true,
    rules: createRequiredTextRule(t('job.form.nameInvalid'), 100),
    componentProps: {
      clearable: true,
      maxlength: 100,
      showCount: true,
      placeholder: t('job.form.namePlaceholder'),
    },
  },
  {
    key: 'job_key',
    path: 'job_key',
    label: t('job.form.key'),
    required: true,
    rules: createRequiredTextRule(t('job.form.keyInvalid'), 100, /^[A-Za-z][A-Za-z0-9_.:-]*$/),
    disabled: props.mode === 'edit',
    componentProps: {
      clearable: true,
      maxlength: 100,
      showCount: true,
      placeholder: t('job.form.keyPlaceholder'),
    },
  },
  {
    key: 'task_name',
    path: 'task_name',
    label: t('job.form.taskName'),
    required: true,
    rules: createRequiredTextRule(t('job.form.taskNameInvalid'), 200),
    feedback: t('job.form.taskNameHelp'),
    showFeedback: true,
    componentProps: {
      clearable: true,
      maxlength: 200,
      showCount: true,
      placeholder: t('job.form.taskNamePlaceholder'),
    },
    span: '1 s:2',
  },
  {
    key: 'cron_expression',
    path: 'cron_expression',
    label: t('job.form.cron'),
    required: true,
    rules: cronRule.value,
    feedback: t('job.form.cronHelp'),
    showFeedback: true,
    componentProps: {
      clearable: true,
      maxlength: 100,
      placeholder: t('job.form.cronPlaceholder'),
    },
    span: '1 s:2',
  },
  {
    key: 'timeout_seconds',
    path: 'timeout_seconds',
    label: t('job.form.timeout'),
    type: 'number',
    required: true,
    rules: createIntegerRule(t('job.form.timeoutInvalid'), 1, 86_400),
    componentProps: {
      min: 1,
      max: 86_400,
      precision: 0,
      placeholder: t('job.form.timeoutPlaceholder'),
    },
  },
  {
    key: 'max_retries',
    path: 'max_retries',
    label: t('job.form.retries'),
    type: 'number',
    required: true,
    rules: createIntegerRule(t('job.form.retriesInvalid'), 0, 10),
    componentProps: {
      min: 0,
      max: 10,
      precision: 0,
      placeholder: t('job.form.retriesPlaceholder'),
    },
  },
  {
    key: 'status',
    path: 'status',
    label: t('job.form.status'),
    type: 'select',
    required: true,
    componentProps: {
      options: statusOptions.value,
      placeholder: t('job.form.statusPlaceholder'),
    },
    span: '1 s:2',
  },
  {
    key: 'args_json',
    path: 'args_json',
    label: t('job.form.arguments'),
    type: 'textarea',
    required: true,
    rules: argumentsRule.value,
    componentProps: {
      class: 'job-json-input',
      maxlength: 10_000,
      rows: 7,
      placeholder: t('job.form.argumentsPlaceholder'),
    },
    span: '1 s:2',
  },
])

const handleCancel = (): void => emit('update:show', false)
const handleSubmit = (model: ScheduledJobFormModel): void => emit('submit', model)
</script>

<template>
  <NModal
    :show="props.show"
    preset="card"
    class="job-form-modal"
    :title="props.mode === 'create' ? t('job.createTitle') : t('job.editTitle')"
    :mask-closable="false"
    @update:show="emit('update:show', $event)"
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
          {{ t('job.action.cancel') }}
        </NButton>
        <NButton
          v-permission="props.mode === 'create' ? 'monitor:job:add' : 'monitor:job:edit'"
          attr-type="button"
          type="primary"
          :loading="actionLoading"
          :disabled="actionLoading"
          @click="submit"
        >
          <template #icon
            ><NIcon><CheckmarkDoneOutline /></NIcon
          ></template>
          {{ t('job.action.save') }}
        </NButton>
      </template>
    </AppForm>
  </NModal>
</template>

<style lang="scss">
.n-card.job-form-modal {
  width: min(820px, calc(100vw - 32px));
}

.job-form-modal .job-json-input textarea {
  font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
}
</style>
