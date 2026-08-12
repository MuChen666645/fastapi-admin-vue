<script setup lang="ts">
import { computed } from 'vue'

import AppSearchForm from '@/components/AppSearchForm/index.vue'
import { useLocale } from '@/hooks'
import type { AppFormField, OnlineSearchPanelProps, OnlineSessionFilters } from '@/types'

defineOptions({ name: 'OnlineSearchPanel' })

const props = defineProps<OnlineSearchPanelProps>()
const emit = defineEmits<{
  search: [filters: OnlineSessionFilters]
  reset: [filters: OnlineSessionFilters]
}>()

const { t } = useLocale()

const fields = computed<ReadonlyArray<AppFormField<OnlineSessionFilters>>>(() => [
  {
    key: 'username',
    path: 'username',
    label: t('online.search.username'),
    componentProps: {
      clearable: true,
      maxlength: 100,
      placeholder: t('online.search.usernamePlaceholder'),
    },
  },
  {
    key: 'ip_address',
    path: 'ip_address',
    label: t('online.search.ipAddress'),
    componentProps: {
      clearable: true,
      maxlength: 64,
      placeholder: t('online.search.ipAddressPlaceholder'),
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
    :search-text="t('online.search.submit')"
    :reset-text="t('online.search.reset')"
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
