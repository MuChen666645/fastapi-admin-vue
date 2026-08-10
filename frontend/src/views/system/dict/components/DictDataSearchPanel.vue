<script setup lang="ts">
import { computed } from 'vue'

import AppSearchForm from '@/components/AppSearchForm/index.vue'
import { useLocale } from '@/hooks'
import type { AppFormField, DictDataListFilters, DictTypeListItem } from '@/types'

defineOptions({ name: 'DictDataSearchPanel' })

interface DictDataSearchPanelProps {
  model: DictDataListFilters
  initialValues: DictDataListFilters
  loading: boolean
  dictTypes: DictTypeListItem[]
}

const props = defineProps<DictDataSearchPanelProps>()
const emit = defineEmits<{
  search: [filters: DictDataListFilters]
  reset: [filters: DictDataListFilters]
}>()

const { t } = useLocale()

const dictTypeOptions = computed(() =>
  props.dictTypes.map((item) => ({ label: item.dict_name, value: item.dict_type })),
)

const statusOptions = computed(() => [
  { label: t('dict.status.all'), value: null },
  { label: t('dict.status.enabled'), value: '1' as const },
  { label: t('dict.status.disabled'), value: '0' as const },
])

const fields = computed<ReadonlyArray<AppFormField<DictDataListFilters>>>(() => [
  {
    key: 'dict_type',
    path: 'dict_type',
    label: t('dict.data.form.type'),
    type: 'select',
    required: true,
    requiredMessage: t('dict.data.search.typeRequired'),
    componentProps: {
      clearable: false,
      filterable: true,
      options: dictTypeOptions.value,
      placeholder: t('dict.data.search.typePlaceholder'),
    },
  },
  {
    key: 'status',
    path: 'status',
    label: t('dict.data.search.status'),
    type: 'select',
    componentProps: {
      clearable: true,
      options: statusOptions.value,
      placeholder: t('dict.data.search.statusPlaceholder'),
    },
  },
])
</script>

<template>
  <AppSearchForm
    :model="props.model"
    :initial-values="props.initialValues"
    :fields="fields"
    :loading="props.loading"
    default-collapsed
    :search-text="t('dict.search.submit')"
    :reset-text="t('dict.search.reset')"
    :layout="{
      labelPlacement: 'top',
      labelWidth: 'auto',
      columns: '1 s:2',
      responsive: 'screen',
      xGap: 16,
      yGap: 4,
      actionAlign: 'end',
    }"
    @search="emit('search', $event)"
    @reset="emit('reset', $event)"
  />
</template>
