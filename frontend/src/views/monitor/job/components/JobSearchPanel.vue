<script setup lang="ts">
import { computed } from 'vue'

import AppSearchForm from '@/components/AppSearchForm/index.vue'
import { useLocale } from '@/hooks'
import type { AppFormField, ScheduledJobFilters, ScheduledJobSearchPanelProps } from '@/types'

defineOptions({ name: 'JobSearchPanel' })

const props = defineProps<ScheduledJobSearchPanelProps>()
const emit = defineEmits<{
  search: [filters: ScheduledJobFilters]
  reset: [filters: ScheduledJobFilters]
}>()
const { t } = useLocale()

const statusOptions = computed(() => [
  { label: t('job.status.all'), value: null },
  { label: t('job.status.enabled'), value: '1' as const },
  { label: t('job.status.disabled'), value: '0' as const },
])

const fields = computed<ReadonlyArray<AppFormField<ScheduledJobFilters>>>(() => [
  {
    key: 'name',
    path: 'name',
    label: t('job.search.name'),
    componentProps: {
      clearable: true,
      maxlength: 100,
      placeholder: t('job.search.namePlaceholder'),
    },
  },
  {
    key: 'status',
    path: 'status',
    label: t('job.search.status'),
    type: 'select',
    componentProps: {
      clearable: true,
      options: statusOptions.value,
      placeholder: t('job.search.statusPlaceholder'),
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
    :search-text="t('job.search.submit')"
    :reset-text="t('job.search.reset')"
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
