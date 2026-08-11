<script setup lang="ts">
import { computed } from 'vue'

import AppSearchForm from '@/components/AppSearchForm/index.vue'
import { useLocale } from '@/hooks'
import type { AppFormField, PostListFilters, PostSearchPanelProps } from '@/types'

defineOptions({ name: 'PostSearchPanel' })

const props = defineProps<PostSearchPanelProps>()
const emit = defineEmits<{
  search: [filters: PostListFilters]
  reset: [filters: PostListFilters]
}>()

const { t } = useLocale()

const statusOptions = computed(() => [
  { label: t('post.status.all'), value: null },
  { label: t('post.status.enabled'), value: '1' as const },
  { label: t('post.status.disabled'), value: '0' as const },
])

const fields = computed<ReadonlyArray<AppFormField<PostListFilters>>>(() => [
  {
    key: 'name',
    path: 'name',
    label: t('post.search.name'),
    componentProps: {
      clearable: true,
      maxlength: 50,
      placeholder: t('post.search.namePlaceholder'),
    },
  },
  {
    key: 'status',
    path: 'status',
    label: t('post.search.status'),
    type: 'select',
    componentProps: {
      clearable: true,
      options: statusOptions.value,
      placeholder: t('post.search.statusPlaceholder'),
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
    :search-text="t('post.search.submit')"
    :reset-text="t('post.search.reset')"
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
