<script setup lang="ts">
import { computed } from 'vue'
import { CheckmarkDoneOutline } from '@vicons/ionicons5'
import { NButton, NIcon, NModal } from 'naive-ui'
import type { FormItemRule } from 'naive-ui'

import AppForm from '@/components/AppForm/index.vue'
import { useLocale } from '@/hooks'
import type { AppFormField, PostFormModalProps, PostFormModel } from '@/types'

defineOptions({ name: 'PostFormModal' })

const props = defineProps<PostFormModalProps>()
const emit = defineEmits<{
  'update:show': [value: boolean]
  submit: [model: PostFormModel]
  reset: []
}>()

const { t } = useLocale()

const statusOptions = computed(() => [
  { label: t('post.status.enabled'), value: '1' as const },
  { label: t('post.status.disabled'), value: '0' as const },
])

const createRequiredTextRule = (message: string): FormItemRule => ({
  required: true,
  validator: (_rule, value: unknown) =>
    typeof value === 'string' && value.trim().length > 0 ? true : new Error(message),
  trigger: ['input', 'blur'],
})

const sortRule = computed<FormItemRule>(() => ({
  required: true,
  validator: (_rule, value: unknown) =>
    typeof value === 'number' && Number.isInteger(value)
      ? true
      : new Error(t('post.form.sortPlaceholder')),
  trigger: ['input', 'blur'],
}))

const fields = computed<ReadonlyArray<AppFormField<PostFormModel>>>(() => [
  {
    key: 'post_code',
    path: 'post_code',
    label: t('post.form.code'),
    required: true,
    rules: createRequiredTextRule(t('post.form.codePlaceholder')),
    componentProps: {
      clearable: true,
      maxlength: 64,
      showCount: true,
      placeholder: t('post.form.codePlaceholder'),
    },
  },
  {
    key: 'post_name',
    path: 'post_name',
    label: t('post.form.name'),
    required: true,
    rules: createRequiredTextRule(t('post.form.namePlaceholder')),
    componentProps: {
      clearable: true,
      maxlength: 50,
      showCount: true,
      placeholder: t('post.form.namePlaceholder'),
    },
  },
  {
    key: 'post_sort',
    path: 'post_sort',
    label: t('post.form.sort'),
    type: 'number',
    required: true,
    rules: sortRule.value,
    componentProps: {
      precision: 0,
      placeholder: t('post.form.sortPlaceholder'),
    },
  },
  {
    key: 'status',
    path: 'status',
    label: t('post.form.status'),
    type: 'select',
    required: true,
    componentProps: {
      options: statusOptions.value,
      placeholder: t('post.form.statusPlaceholder'),
    },
  },
  {
    key: 'remark',
    path: 'remark',
    label: t('post.form.remark'),
    type: 'textarea',
    componentProps: {
      clearable: true,
      maxlength: 500,
      showCount: true,
      rows: 4,
      placeholder: t('post.form.remarkPlaceholder'),
    },
    span: '1 s:2',
  },
])

const handleShowUpdate = (value: boolean): void => emit('update:show', value)
const handleCancel = (): void => emit('update:show', false)
const handleSubmit = (model: PostFormModel): void => emit('submit', model)
</script>

<template>
  <NModal
    :show="props.show"
    preset="card"
    class="post-modal"
    :title="props.mode === 'create' ? t('post.createTitle') : t('post.editTitle')"
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
          {{ t('post.form.cancel') }}
        </NButton>
        <NButton
          v-permission="props.mode === 'create' ? 'system:post:add' : 'system:post:edit'"
          attr-type="button"
          type="primary"
          :loading="actionLoading"
          :disabled="actionLoading"
          @click="submit"
        >
          <template #icon>
            <NIcon><CheckmarkDoneOutline /></NIcon>
          </template>
          {{ t('post.form.save') }}
        </NButton>
      </template>
    </AppForm>
  </NModal>
</template>

<style lang="scss">
.n-card.post-modal {
  width: min(720px, calc(100vw - 32px));
}
</style>
