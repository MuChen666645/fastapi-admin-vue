<script setup lang="ts">
import { computed } from 'vue'

import AppSearchForm from '@/components/AppSearchForm/index.vue'
import { useLocale } from '@/hooks'
import type { AppFormField, MessageListFilters, MessageViewMode, MyMessageFilters } from '@/types'

defineOptions({ name: 'MessageSearchPanel' })

interface MessageSearchPanelProps {
  mode: MessageViewMode
  managementModel: MessageListFilters
  managementInitialValues: MessageListFilters
  inboxModel: MyMessageFilters
  inboxInitialValues: MyMessageFilters
  managementLoading: boolean
  inboxLoading: boolean
}

const props = defineProps<MessageSearchPanelProps>()

const emit = defineEmits<{
  'manage-search': [filters: MessageListFilters]
  'inbox-search': [filters: MyMessageFilters]
}>()

const { t } = useLocale()

const messageTypeOptions = computed(() => [
  { label: t('message.type.system'), value: 'system' as const },
  { label: t('message.type.approval'), value: 'approval' as const },
  { label: t('message.type.alarm'), value: 'alarm' as const },
])

const statusOptions = computed(() => [
  { label: t('message.status.all'), value: null },
  { label: t('message.status.enabled'), value: '1' as const },
  { label: t('message.status.disabled'), value: '0' as const },
])

const readStatusOptions = computed(() => [
  { label: t('message.filter.all'), value: 'all' as const },
  { label: t('message.filter.unread'), value: 'unread' as const },
  { label: t('message.filter.read'), value: 'read' as const },
])

const messageSearchFields = computed<ReadonlyArray<AppFormField<MessageListFilters>>>(() => [
  {
    key: 'title',
    path: 'title',
    label: t('message.search.title'),
    componentProps: {
      clearable: true,
      placeholder: t('message.search.titlePlaceholder'),
    },
  },
  {
    key: 'content',
    path: 'content',
    label: t('message.search.content'),
    componentProps: {
      clearable: true,
      placeholder: t('message.search.contentPlaceholder'),
    },
  },
  {
    key: 'message_type',
    path: 'message_type',
    label: t('message.search.type'),
    type: 'select',
    componentProps: {
      clearable: true,
      options: messageTypeOptions.value,
      placeholder: t('message.search.typePlaceholder'),
    },
  },
  {
    key: 'status',
    path: 'status',
    label: t('message.search.status'),
    type: 'select',
    componentProps: {
      clearable: true,
      options: statusOptions.value,
      placeholder: t('message.search.statusPlaceholder'),
    },
  },
  {
    key: 'publish_time',
    path: 'publish_time',
    label: t('message.search.publishTime'),
    type: 'date',
    componentProps: {
      type: 'daterange',
      clearable: true,
      format: 'yyyy-MM-dd',
      startPlaceholder: t('message.search.startDate'),
      endPlaceholder: t('message.search.endDate'),
    },
  },
])

const mySearchFields = computed<ReadonlyArray<AppFormField<MyMessageFilters>>>(() => [
  {
    key: 'keyword',
    path: 'keyword',
    label: t('message.search.keyword'),
    componentProps: {
      clearable: true,
      placeholder: t('message.search.titlePlaceholder'),
    },
  },
  {
    key: 'message_type',
    path: 'message_type',
    label: t('message.search.type'),
    type: 'select',
    componentProps: {
      clearable: true,
      options: messageTypeOptions.value,
      placeholder: t('message.search.typePlaceholder'),
    },
  },
  {
    key: 'read_status',
    path: 'read_status',
    label: t('message.filter.readStatus'),
    type: 'select',
    componentProps: { options: readStatusOptions.value },
  },
  {
    key: 'publish_time',
    path: 'publish_time',
    label: t('message.search.publishTime'),
    type: 'date',
    componentProps: {
      type: 'daterange',
      clearable: true,
      format: 'yyyy-MM-dd',
      startPlaceholder: t('message.search.startDate'),
      endPlaceholder: t('message.search.endDate'),
    },
  },
])

const handleManagementSearch = (filters: MessageListFilters): void => {
  emit('manage-search', filters)
}

const handleInboxSearch = (filters: MyMessageFilters): void => {
  emit('inbox-search', filters)
}
</script>

<template>
  <AppSearchForm
    v-if="props.mode === 'manage'"
    :model="props.managementModel"
    :initial-values="props.managementInitialValues"
    :fields="messageSearchFields"
    :loading="props.managementLoading"
    default-collapsed
    :search-text="t('message.search.submit')"
    :reset-text="t('message.search.reset')"
    :layout="{
      labelPlacement: 'top',
      labelWidth: 'auto',
      columns: '1 s:2 m:4',
      responsive: 'screen',
      xGap: 16,
      yGap: 4,
      actionAlign: 'end',
    }"
    @search="handleManagementSearch"
    @reset="handleManagementSearch"
  />

  <AppSearchForm
    v-else
    :model="props.inboxModel"
    :initial-values="props.inboxInitialValues"
    :fields="mySearchFields"
    :loading="props.inboxLoading"
    default-collapsed
    :search-text="t('message.search.submit')"
    :reset-text="t('message.search.reset')"
    :layout="{
      labelPlacement: 'top',
      labelWidth: 'auto',
      columns: '1 s:2 m:4',
      responsive: 'screen',
      xGap: 16,
      yGap: 4,
      actionAlign: 'end',
    }"
    @search="handleInboxSearch"
    @reset="handleInboxSearch"
  />
</template>
