<script setup lang="ts">
import { computed } from 'vue'

import AppSearchForm from '@/components/AppSearchForm/index.vue'
import { useLocale } from '@/hooks'
import type { AppFormField, MenuListFilters } from '@/types'

defineOptions({ name: 'MenuSearchPanel' })

interface MenuSearchPanelProps {
  model: MenuListFilters
  initialValues: MenuListFilters
  loading: boolean
}

const props = defineProps<MenuSearchPanelProps>()
const emit = defineEmits<{
  search: [filters: MenuListFilters]
  reset: [filters: MenuListFilters]
}>()

const { t } = useLocale()

const statusOptions = computed(() => [
  { label: t('menuManagement.status.all'), value: null },
  { label: t('menuManagement.status.enabled'), value: '1' as const },
  { label: t('menuManagement.status.disabled'), value: '0' as const },
])

const fields = computed<ReadonlyArray<AppFormField<MenuListFilters>>>(() => [
  {
    key: 'menu_name',
    path: 'menu_name',
    label: t('menuManagement.search.name'),
    componentProps: {
      clearable: true,
      placeholder: t('menuManagement.search.namePlaceholder'),
    },
  },
  {
    key: 'status',
    path: 'status',
    label: t('menuManagement.search.status'),
    type: 'select',
    componentProps: {
      clearable: true,
      options: statusOptions.value,
      placeholder: t('menuManagement.search.statusPlaceholder'),
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
    :search-text="t('menuManagement.search.submit')"
    :reset-text="t('menuManagement.search.reset')"
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
