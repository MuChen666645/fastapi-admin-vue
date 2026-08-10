<script setup lang="ts">
import { computed } from 'vue'
import { CheckmarkDoneOutline } from '@vicons/ionicons5'
import { NButton, NIcon, NModal } from 'naive-ui'

import AppForm from '@/components/AppForm/index.vue'
import { useLocale } from '@/hooks'
import type { AppFormField, DictDataFormModel, DictTypeListItem, DictionaryFormMode } from '@/types'

defineOptions({ name: 'DictDataFormModal' })

interface DictDataFormModalProps {
  show: boolean
  mode: DictionaryFormMode
  model: DictDataFormModel
  loading: boolean
  dictTypes: DictTypeListItem[]
}

const props = defineProps<DictDataFormModalProps>()
const emit = defineEmits<{
  'update:show': [value: boolean]
  submit: [model: DictDataFormModel]
  reset: []
}>()

const { t } = useLocale()

const statusOptions = computed(() => [
  { label: t('dict.status.enabled'), value: '1' as const },
  { label: t('dict.status.disabled'), value: '0' as const },
])

const dictTypeOptions = computed(() =>
  props.dictTypes.map((item) => ({ label: item.dict_name, value: item.dict_type })),
)

const fields = computed<ReadonlyArray<AppFormField<DictDataFormModel>>>(() => [
  {
    key: 'dict_sort',
    path: 'dict_sort',
    label: t('dict.data.form.sort'),
    type: 'number',
    required: true,
    requiredMessage: t('dict.data.form.sortPlaceholder'),
    componentProps: {
      min: 0,
      placeholder: t('dict.data.form.sortPlaceholder'),
    },
  },
  {
    key: 'dict_label',
    path: 'dict_label',
    label: t('dict.data.form.label'),
    required: true,
    requiredMessage: t('dict.data.form.labelPlaceholder'),
    componentProps: {
      clearable: true,
      placeholder: t('dict.data.form.labelPlaceholder'),
    },
  },
  {
    key: 'dict_value',
    path: 'dict_value',
    label: t('dict.data.form.value'),
    required: true,
    requiredMessage: t('dict.data.form.valuePlaceholder'),
    componentProps: {
      clearable: true,
      placeholder: t('dict.data.form.valuePlaceholder'),
    },
  },
  {
    key: 'dict_type',
    path: 'dict_type',
    label: t('dict.data.form.type'),
    type: 'select',
    required: true,
    requiredMessage: t('dict.data.form.typePlaceholder'),
    componentProps: {
      filterable: true,
      options: dictTypeOptions.value,
      placeholder:
        dictTypeOptions.value.length > 0
          ? t('dict.data.form.typePlaceholder')
          : t('dict.data.form.noTypes'),
    },
  },
  {
    key: 'status',
    path: 'status',
    label: t('dict.data.form.status'),
    type: 'select',
    required: true,
    requiredMessage: t('dict.data.form.statusPlaceholder'),
    componentProps: {
      options: statusOptions.value,
      placeholder: t('dict.data.form.statusPlaceholder'),
    },
  },
  {
    key: 'remark',
    path: 'remark',
    label: t('dict.data.form.remark'),
    type: 'textarea',
    componentProps: {
      clearable: true,
      rows: 4,
      placeholder: t('dict.data.form.remarkPlaceholder'),
    },
    span: '1 s:2',
  },
])

const handleShowUpdate = (value: boolean): void => emit('update:show', value)
const handleCancel = (): void => emit('update:show', false)
const handleSubmit = (model: DictDataFormModel): void => emit('submit', model)
</script>

<template>
  <NModal
    :show="props.show"
    preset="card"
    class="dict-modal"
    :title="props.mode === 'create' ? t('dict.data.createTitle') : t('dict.data.editTitle')"
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
