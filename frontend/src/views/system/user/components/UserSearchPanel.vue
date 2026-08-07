<script setup lang="ts">
import { computed } from 'vue'

import AppSearchForm from '@/components/AppSearchForm/index.vue'
import { useLocale } from '@/hooks'
import type { AppFormField, UserListFilters } from '@/types'

defineOptions({ name: 'UserSearchPanel' })

interface UserSearchPanelProps {
  model: UserListFilters
  initialValues: UserListFilters
  loading: boolean
}

const props = defineProps<UserSearchPanelProps>()

const emit = defineEmits<{
  search: [filters: UserListFilters]
  reset: [filters: UserListFilters]
}>()

const { t } = useLocale()

const fields = computed<ReadonlyArray<AppFormField<UserListFilters>>>(() => [
  {
    key: 'username',
    path: 'username',
    label: t('user.search.username'),
    componentProps: {
      clearable: true,
      placeholder: t('user.form.usernamePlaceholder'),
    },
  },
  {
    key: 'nickname',
    path: 'nickname',
    label: t('user.search.nickname'),
    componentProps: {
      clearable: true,
      placeholder: t('user.form.nicknamePlaceholder'),
    },
  },
  {
    key: 'phone',
    path: 'phone',
    label: t('user.search.phone'),
    componentProps: {
      clearable: true,
      placeholder: t('user.form.phonePlaceholder'),
    },
  },
  {
    key: 'email',
    path: 'email',
    label: t('user.search.email'),
    componentProps: {
      clearable: true,
      placeholder: t('user.form.emailPlaceholder'),
    },
  },
  {
    key: 'create_time',
    path: 'create_time',
    label: t('user.search.createTime'),
    type: 'date',
    componentProps: {
      type: 'daterange',
      clearable: true,
      format: 'yyyy-MM-dd',
      startPlaceholder: t('user.search.startDate'),
      endPlaceholder: t('user.search.endDate'),
    },
  },
])

const handleSearch = (filters: UserListFilters): void => {
  emit('search', filters)
}

const handleReset = (filters: UserListFilters): void => {
  emit('reset', filters)
}
</script>

<template>
  <AppSearchForm
    :model="props.model"
    :initial-values="props.initialValues"
    :fields="fields"
    :loading="props.loading"
    default-collapsed
    :search-text="t('user.search.submit')"
    :reset-text="t('user.search.reset')"
    :layout="{
      labelPlacement: 'top',
      labelWidth: 'auto',
      columns: '1 s:2 m:4',
      responsive: 'screen',
      xGap: 16,
      yGap: 4,
      actionAlign: 'end',
    }"
    @search="handleSearch"
    @reset="handleReset"
  />
</template>
