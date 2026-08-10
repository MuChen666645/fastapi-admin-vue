<script setup lang="ts">
import { computed } from 'vue'
import { CheckmarkDoneOutline } from '@vicons/ionicons5'
import { NButton, NIcon, NModal } from 'naive-ui'

import AppForm from '@/components/AppForm/index.vue'
import { useLocale } from '@/hooks'
import type { AppFormField, DictTypeFormModel, DictionaryFormMode } from '@/types'

defineOptions({ name: 'DictTypeFormModal' })

interface DictTypeFormModalProps {
  show: boolean
  mode: DictionaryFormMode
  model: DictTypeFormModel
  loading: boolean
}

const props = defineProps<DictTypeFormModalProps>()
const emit = defineEmits<{
  'update:show': [value: boolean]
  submit: [model: DictTypeFormModel]
  reset: []
}>()

const { t } = useLocale()

const statusOptions = computed(() => [
  { label: t('dict.status.enabled'), value: '1' as const },
  { label: t('dict.status.disabled'), value: '0' as const },
])

const fields = computed<ReadonlyArray<AppFormField<DictTypeFormModel>>>(() => [
  {
    key: 'dict_name',
    path: 'dict_name',
    label: t('dict.type.form.name'),
    required: true,
    requiredMessage: t('dict.type.form.namePlaceholder'),
    componentProps: {
      clearable: true,
      placeholder: t('dict.type.form.namePlaceholder'),
    },
  },
  {
    key: 'dict_type',
    path: 'dict_type',
    label: t('dict.type.form.code'),
    required: true,
    requiredMessage: t('dict.type.form.codePlaceholder'),
    componentProps: {
      clearable: true,
      placeholder: t('dict.type.form.codePlaceholder'),
    },
  },
  {
    key: 'status',
    path: 'status',
    label: t('dict.type.form.status'),
    type: 'select',
    required: true,
    requiredMessage: t('dict.type.form.statusPlaceholder'),
    componentProps: {
      options: statusOptions.value,
      placeholder: t('dict.type.form.statusPlaceholder'),
    },
  },
  {
    key: 'remark',
    path: 'remark',
    label: t('dict.type.form.remark'),
    type: 'textarea',
    componentProps: {
      clearable: true,
      rows: 4,
      placeholder: t('dict.type.form.remarkPlaceholder'),
    },
    span: '1 s:2',
  },
])

const handleShowUpdate = (value: boolean): void => emit('update:show', value)
const handleCancel = (): void => emit('update:show', false)
const handleSubmit = (model: DictTypeFormModel): void => emit('submit', model)
</script>

<template>
  <NModal
    :show="props.show"
    preset="card"
    class="dict-modal"
    :title="props.mode === 'create' ? t('dict.type.createTitle') : t('dict.type.editTitle')"
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
          {{ t('dict.form.cancel') }}
        </NButton>
        <NButton
          v-permission="props.mode === 'create' ? 'system:dict:add' : 'system:dict:edit'"
          attr-type="button"
          type="primary"
          :loading="actionLoading"
          :disabled="actionLoading"
          @click="submit"
        >
          <template #icon
            ><NIcon><CheckmarkDoneOutline /></NIcon
          ></template>
          {{ t('dict.form.save') }}
        </NButton>
      </template>
    </AppForm>
  </NModal>
</template>

<style lang="scss">
.n-card.dict-modal {
  width: min(700px, calc(100vw - 32px));
}
</style>
