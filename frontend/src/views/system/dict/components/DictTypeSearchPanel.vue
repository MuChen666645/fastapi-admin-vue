<script setup lang="ts">
import { computed } from 'vue'

import AppSearchForm from '@/components/AppSearchForm/index.vue'
import { useLocale } from '@/hooks'
import type { AppFormField, DictTypeListFilters } from '@/types'

defineOptions({ name: 'DictTypeSearchPanel' })

interface DictTypeSearchPanelProps {
  model: DictTypeListFilters
  initialValues: DictTypeListFilters
  loading: boolean
}

const props = defineProps<DictTypeSearchPanelProps>()
const emit = defineEmits<{
  search: [filters: DictTypeListFilters]
  reset: [filters: DictTypeListFilters]
}>()

const { t } = useLocale()

const statusOptions = computed(() => [
  { label: t('dict.status.all'), value: null },
  { label: t('dict.status.enabled'), value: '1' as const },
  { label: t('dict.status.disabled'), value: '0' as const },
])

const fields = computed<ReadonlyArray<AppFormField<DictTypeListFilters>>>(() => [
  {
    key: 'name',
    path: 'name',
    label: t('dict.type.search.name'),
    componentProps: {
      clearable: true,
      placeholder: t('dict.type.search.namePlaceholder'),
    },
  },
  {
    key: 'status',
    path: 'status',
    label: t('dict.type.search.status'),
    type: 'select',
    componentProps: {
      clearable: true,
      options: statusOptions.value,
      placeholder: t('dict.type.search.statusPlaceholder'),
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
