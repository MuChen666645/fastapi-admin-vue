<script setup lang="ts">
import { computed, h } from 'vue'
import {
  AlertCircleOutline,
  ClipboardOutline,
  CreateOutline,
  EyeOutline,
  InformationCircleOutline,
  TrashOutline,
} from '@vicons/ionicons5'
import { NButton, NDataTable, NEmpty, NIcon, NTag } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'

import { useLocale } from '@/hooks'
import type { MessageItem, MessageListItem, MessageType, MessageViewMode } from '@/types'
import { resolveMessageTone } from '@/utils'

defineOptions({ name: 'MessageTable' })

interface MessageTableProps {
  mode: MessageViewMode
  managementData: MessageListItem[]
  inboxData: MessageItem[]
  managementLoading: boolean
  inboxLoading: boolean
  canQuery: boolean
  canEdit: boolean
  canDelete: boolean
}

const props = defineProps<MessageTableProps>()

const emit = defineEmits<{
  'manage-detail': [item: MessageListItem]
  edit: [item: MessageListItem]
  delete: [item: MessageListItem]
  'inbox-detail': [item: MessageItem]
}>()

const { t } = useLocale()

const getMessageTagType = (messageType: MessageType) => {
  const tone = resolveMessageTone(messageType)
  if (tone === 'danger') {
    return 'error'
  }

  if (tone === 'warning') {
    return 'warning'
  }

  return 'info'
}

const getMessageIcon = (messageType: MessageType) => {
  const tone = resolveMessageTone(messageType)
  if (tone === 'danger') {
    return AlertCircleOutline
  }

  if (tone === 'warning') {
    return ClipboardOutline
  }

  return InformationCircleOutline
}

const getMessageTypeLabel = (messageType: MessageType): string => {
  const labels: Record<MessageType, string> = {
    system: t('message.type.system'),
    approval: t('message.type.approval'),
    alarm: t('message.type.alarm'),
  }
  return labels[messageType]
}

const renderMessageTypeTag = (messageType: MessageType) =>
  h(
    NTag,
    {
      class: 'message-type-tag',
      type: getMessageTagType(messageType),
      size: 'small',
      round: true,
    },
    {
      default: () => [
        h(
          NIcon,
          { size: 14, 'aria-hidden': 'true' },
          { default: () => h(getMessageIcon(messageType)) },
        ),
        h('span', { class: 'message-type-label' }, getMessageTypeLabel(messageType)),
      ],
    },
  )

const getStatusLabel = (status: MessageListItem['status']): string =>
  status === '1' ? t('message.status.enabled') : t('message.status.disabled')

const getReadStatusLabel = (readAt: string | null): string =>
  readAt ? t('message.read') : t('message.unread')

const formatTimestamp = (value: string | null): string => value ?? t('message.noTime')

const managementColumns = computed<DataTableColumns<MessageListItem>>(() => [
  {
    title: t('message.column.title'),
    key: 'message_title',
    minWidth: 220,
    ellipsis: { tooltip: true },
  },
  {
    title: t('message.column.type'),
    key: 'message_type',
    width: 140,
    render: (item) => renderMessageTypeTag(item.message_type),
  },
  {
    title: t('message.column.content'),
    key: 'message_content',
    minWidth: 320,
    ellipsis: { tooltip: true },
  },
  {
    title: t('message.column.status'),
    key: 'status',
    width: 110,
    render: (item) =>
      h(
        NTag,
        { type: item.status === '1' ? 'success' : 'default', size: 'small' },
        { default: () => getStatusLabel(item.status) },
      ),
  },
  {
    title: t('message.column.publishTime'),
    key: 'publish_time',
    width: 180,
    render: (item) => formatTimestamp(item.publish_time),
  },
  {
    title: t('message.column.action'),
    key: 'action',
    width: 150,
    render: (item) =>
      h('div', { class: 'message-row-actions' }, [
        ...(props.canQuery
          ? [
              h(
                NButton,
                {
                  quaternary: true,
                  circle: true,
                  'aria-label': t('message.action.detail'),
                  title: t('message.action.detail'),
                  onClick: () => emit('manage-detail', item),
                },
                { icon: () => h(NIcon, null, { default: () => h(EyeOutline) }) },
              ),
            ]
          : []),
        ...(props.canEdit
          ? [
              h(
                NButton,
                {
                  quaternary: true,
                  circle: true,
                  'aria-label': t('message.action.edit'),
                  title: t('message.action.edit'),
                  onClick: () => emit('edit', item),
                },
                { icon: () => h(NIcon, null, { default: () => h(CreateOutline) }) },
              ),
            ]
          : []),
        ...(props.canDelete
          ? [
              h(
                NButton,
                {
                  quaternary: true,
                  circle: true,
                  type: 'error',
                  'aria-label': t('message.action.delete'),
                  title: t('message.action.delete'),
                  onClick: () => emit('delete', item),
                },
                { icon: () => h(NIcon, null, { default: () => h(TrashOutline) }) },
              ),
            ]
          : []),
      ]),
  },
])

const inboxColumns = computed<DataTableColumns<MessageItem>>(() => [
  {
    title: t('message.column.title'),
    key: 'message_title',
    minWidth: 220,
    ellipsis: { tooltip: true },
  },
  {
    title: t('message.column.type'),
    key: 'message_type',
    width: 140,
    render: (item) => renderMessageTypeTag(item.message_type),
  },
  {
    title: t('message.column.content'),
    key: 'message_content',
    minWidth: 320,
    ellipsis: { tooltip: true },
  },
  {
    title: t('message.column.readStatus'),
    key: 'read_at',
    width: 110,
    render: (item) =>
      h(
        NTag,
        { type: item.read_at ? 'default' : 'info', size: 'small' },
        { default: () => getReadStatusLabel(item.read_at) },
      ),
  },
  {
    title: t('message.column.publishTime'),
    key: 'publish_time',
    width: 180,
    render: (item) => formatTimestamp(item.publish_time),
  },
  {
    title: t('message.column.action'),
    key: 'action',
    width: 150,
    render: (item) =>
      h(
        NButton,
        {
          text: true,
          type: 'primary',
          onClick: () => emit('inbox-detail', item),
        },
        { default: () => t('message.action.detail') },
      ),
  },
])

const rowKey = (item: MessageListItem | MessageItem): number => item.id
</script>

<template>
  <NDataTable
    v-if="props.mode === 'manage'"
    :columns="managementColumns"
    :data="props.managementData"
    :loading="props.managementLoading"
    :scroll-x="1120"
    remote
    :row-key="rowKey"
  >
    <template #empty><NEmpty :description="t('message.empty')" /></template>
  </NDataTable>

  <NDataTable
    v-else
    :columns="inboxColumns"
    :data="props.inboxData"
    :loading="props.inboxLoading"
    :scroll-x="1120"
    remote
    :row-key="rowKey"
  >
    <template #empty><NEmpty :description="t('message.empty')" /></template>
  </NDataTable>
</template>

<style lang="scss" scoped>
.message-type-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  vertical-align: middle;
}

.message-type-tag :deep(.n-icon) {
  display: inline-flex;
  align-items: center;
  vertical-align: middle;
}

.message-type-label {
  line-height: 1;
}

.message-row-actions {
  display: flex;
  align-items: center;
  gap: 2px;
}
</style>
