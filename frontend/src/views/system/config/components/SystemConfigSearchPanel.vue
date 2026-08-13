<script setup lang="ts">
import { computed } from 'vue'

import AppSearchForm from '@/components/AppSearchForm/index.vue'
import { useLocale } from '@/hooks'
import type { AppFormField, SystemConfigFilters, SystemConfigSearchPanelProps } from '@/types'

defineOptions({ name: 'SystemConfigSearchPanel' })

const props = defineProps<SystemConfigSearchPanelProps>()
const emit = defineEmits<{
  search: [filters: SystemConfigFilters]
  reset: [filters: SystemConfigFilters]
}>()

const { t } = useLocale()

const fields = computed<ReadonlyArray<AppFormField<SystemConfigFilters>>>(() => [
  {
    key: 'name',
    path: 'name',
    label: t('systemConfig.search.name'),
    componentProps: {
      clearable: true,
      maxlength: 100,
      placeholder: t('systemConfig.search.namePlaceholder'),
    },
  },
  {
    key: 'key',
    path: 'key',
    label: t('systemConfig.search.key'),
    componentProps: {
      clearable: true,
      maxlength: 100,
      placeholder: t('systemConfig.search.keyPlaceholder'),
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
    :search-text="t('systemConfig.search.submit')"
    :reset-text="t('systemConfig.search.reset')"
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
