<script setup lang="ts">
import { computed } from 'vue'

import AppSearchForm from '@/components/AppSearchForm/index.vue'
import { useLocale } from '@/hooks'
import type { AppFormField, LogListFilters, LogSearchPanelProps } from '@/types'

defineOptions({ name: 'LogSearchPanel' })

const props = defineProps<LogSearchPanelProps>()
const emit = defineEmits<{
  search: [filters: LogListFilters]
  reset: [filters: LogListFilters]
}>()

const { t } = useLocale()

const statusOptions = computed(() => [
  { label: t('log.status.all'), value: null },
  { label: t('log.status.success'), value: '1' as const },
  { label: t('log.status.failed'), value: '0' as const },
])

const fields = computed<ReadonlyArray<AppFormField<LogListFilters>>>(() => {
  const usernameField: AppFormField<LogListFilters> = {
    key: 'username',
    path: 'username',
    label: t('log.search.username'),
    componentProps: {
      clearable: true,
      placeholder: t('log.search.usernamePlaceholder'),
    },
  }
  const pathField: AppFormField<LogListFilters> = {
    key: 'path',
    path: 'path',
    label: t('log.search.path'),
    componentProps: {
      clearable: true,
      placeholder: t('log.search.pathPlaceholder'),
    },
  }
  const timeRangeField: AppFormField<LogListFilters> = {
    key: 'time_range',
    path: 'time_range',
    label: t('log.search.timeRange'),
    type: 'date',
    componentProps: {
      type: 'daterange',
      clearable: true,
      format: 'yyyy-MM-dd',
      startPlaceholder: t('log.search.startDate'),
      endPlaceholder: t('log.search.endDate'),
    },
  }

  if (props.activeType !== 'login') {
    return [usernameField, pathField, timeRangeField]
  }

  return [
    usernameField,
    timeRangeField,
    {
      key: 'status',
      path: 'status',
      label: t('log.search.status'),
      type: 'select',
      componentProps: {
        clearable: true,
        options: statusOptions.value,
        placeholder: t('log.search.statusPlaceholder'),
      },
    },
  ]
})
</script>

<template>
  <AppSearchForm
    :model="props.model"
    :initial-values="props.initialValues"
    :fields="fields"
    :loading="props.loading"
    default-collapsed
    :search-text="t('log.search.submit')"
    :reset-text="t('log.search.reset')"
    :layout="{
      labelPlacement: 'top',
      labelWidth: 'auto',
      columns: '1 s:2 m:4',
      responsive: 'screen',
      xGap: 16,
      yGap: 4,
      actionAlign: 'end',
    }"
    @search="emit('search', $event)"
    @reset="emit('reset', $event)"
  />
</template>
