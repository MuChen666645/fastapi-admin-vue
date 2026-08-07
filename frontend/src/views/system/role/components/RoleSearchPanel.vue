<script setup lang="ts">
import { computed } from 'vue'

import AppSearchForm from '@/components/AppSearchForm/index.vue'
import { useLocale } from '@/hooks'
import type { AppFormField, RoleListFilters } from '@/types'

defineOptions({ name: 'RoleSearchPanel' })

interface RoleSearchPanelProps {
  model: RoleListFilters
  initialValues: RoleListFilters
  loading: boolean
}

const props = defineProps<RoleSearchPanelProps>()
const emit = defineEmits<{
  search: [filters: RoleListFilters]
  reset: [filters: RoleListFilters]
}>()

const { t } = useLocale()

const fields = computed<ReadonlyArray<AppFormField<RoleListFilters>>>(() => [
  {
    key: 'name',
    path: 'name',
    label: t('role.search.name'),
    componentProps: {
      clearable: true,
      placeholder: t('role.search.namePlaceholder'),
    },
  },
  {
    key: 'code',
    path: 'code',
    label: t('role.search.code'),
    componentProps: {
      clearable: true,
      placeholder: t('role.search.codePlaceholder'),
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
    :search-text="t('role.search.submit')"
    :reset-text="t('role.search.reset')"
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
