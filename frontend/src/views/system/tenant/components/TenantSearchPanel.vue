<script setup lang="ts">
import { computed } from 'vue'

import AppSearchForm from '@/components/AppSearchForm/index.vue'
import { useLocale } from '@/hooks'
import type { AppFormField, TenantFilters, TenantSearchPanelProps } from '@/types'

defineOptions({ name: 'TenantSearchPanel' })

const props = defineProps<TenantSearchPanelProps>()
const emit = defineEmits<{
  search: [filters: TenantFilters]
  reset: [filters: TenantFilters]
}>()
const { t } = useLocale()

const statusOptions = computed(() => [
  { label: t('tenant.status.enabled'), value: '1' as const },
  { label: t('tenant.status.disabled'), value: '0' as const },
])

const fields = computed<ReadonlyArray<AppFormField<TenantFilters>>>(() => [
  {
    key: 'code',
    path: 'code',
    label: t('tenant.search.code'),
    componentProps: {
      clearable: true,
      maxlength: 64,
      placeholder: t('tenant.search.codePlaceholder'),
    },
  },
  {
    key: 'name',
    path: 'name',
    label: t('tenant.search.name'),
    componentProps: {
      clearable: true,
      maxlength: 100,
      placeholder: t('tenant.search.namePlaceholder'),
    },
  },
  {
    key: 'status',
    path: 'status',
    label: t('tenant.search.status'),
    type: 'select',
    componentProps: {
      clearable: true,
      options: statusOptions.value,
      placeholder: t('tenant.search.statusPlaceholder'),
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
    :search-text="t('tenant.search.submit')"
    :reset-text="t('tenant.search.reset')"
    :layout="{
      labelPlacement: 'top',
      labelWidth: 'auto',
      columns: '1 s:2 m:3',
      responsive: 'screen',
      xGap: 16,
      yGap: 4,
      actionAlign: 'end',
    }"
    @search="emit('search', $event)"
    @reset="emit('reset', $event)"
  />
</template>
