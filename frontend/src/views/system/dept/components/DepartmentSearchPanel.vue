<script setup lang="ts">
import { computed } from 'vue'

import AppSearchForm from '@/components/AppSearchForm/index.vue'
import { useLocale } from '@/hooks'
import type { AppFormField, DepartmentListFilters, DepartmentSearchPanelProps } from '@/types'

defineOptions({ name: 'DepartmentSearchPanel' })

const props = defineProps<DepartmentSearchPanelProps>()
const emit = defineEmits<{
  search: [filters: DepartmentListFilters]
  reset: [filters: DepartmentListFilters]
}>()

const { t } = useLocale()

const statusOptions = computed(() => [
  { label: t('department.status.all'), value: null },
  { label: t('department.status.enabled'), value: '1' as const },
  { label: t('department.status.disabled'), value: '0' as const },
])

const fields = computed<ReadonlyArray<AppFormField<DepartmentListFilters>>>(() => [
  {
    key: 'name',
    path: 'name',
    label: t('department.search.name'),
    componentProps: {
      clearable: true,
      maxlength: 50,
      placeholder: t('department.search.namePlaceholder'),
    },
  },
  {
    key: 'status',
    path: 'status',
    label: t('department.search.status'),
    type: 'select',
    componentProps: {
      clearable: true,
      options: statusOptions.value,
      placeholder: t('department.search.statusPlaceholder'),
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
    :search-text="t('department.search.submit')"
    :reset-text="t('department.search.reset')"
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
