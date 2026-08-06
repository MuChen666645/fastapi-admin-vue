<script setup lang="ts">
import { computed, h, onMounted, reactive, ref, watch } from 'vue'
import {
  AddOutline,
  AlertCircleOutline,
  CheckmarkDoneOutline,
  ClipboardOutline,
  CreateOutline,
  EyeOutline,
  InformationCircleOutline,
  NotificationsOutline,
  RefreshOutline,
  TrashOutline,
} from '@vicons/ionicons5'
import {
  NAlert,
  NButton,
  NDataTable,
  NDatePicker,
  NDivider,
  NEmpty,
  NForm,
  NFormItem,
  NIcon,
  NInput,
  NModal,
  NPagination,
  NSelect,
  NSpin,
  NRadioButton,
  NRadioGroup,
  NTag,
  useDialog,
  useMessage,
} from 'naive-ui'
import type { DataTableColumns, FormInst, FormRules } from 'naive-ui'
import { useRoute } from 'vue-router'

import {
  createMessage,
  deleteMessage,
  fetchMessageDetail,
  fetchMessageList,
  fetchMyMessageDetail,
  fetchMyMessageList,
  markMessageRead,
  updateMessage,
} from '@/api'
import AppSearchForm from '@/components/AppSearchForm/index.vue'
import { useLocale, usePagination, usePermission } from '@/hooks'
import { useMessageStore } from '@/stores'
import type {
  AppFormField,
  MessageCreatePayload,
  MessageDetailView,
  MessageFormModel,
  MessageItem,
  MessageListFilters,
  MessageListItem,
  MessageStatus,
  MessageType,
  MessageUpdatePayload,
  MessageViewMode,
  MyMessageFilters,
  TranslationKey,
} from '@/types'
import {
  parseRecipientUserIds,
  resolveMessageTone,
  toMessageFormTime,
  toMessagePublishTime,
} from '@/utils'

defineOptions({ name: 'SystemMessageView' })

const route = useRoute()
const messageStore = useMessageStore()
const dialog = useDialog()
const message = useMessage()
const { t } = useLocale()
const { hasPermission } = usePermission()

const viewMode = ref<MessageViewMode>('inbox')
const canManage = computed(() => hasPermission('system:message:list'))
const canCreate = computed(() => hasPermission('system:message:add'))
const canQuery = computed(() => hasPermission('system:message:query'))
const canEdit = computed(() => hasPermission('system:message:edit'))
const canDelete = computed(() => hasPermission('system:message:remove'))

const createInitialMessageFilters = (): MessageListFilters => ({
  title: '',
  content: '',
  message_type: null,
  status: null,
  publish_time: null,
})

const createInitialMyFilters = (): MyMessageFilters => ({
  keyword: '',
  message_type: null,
  read_status: 'all',
  publish_time: null,
})

const messageFilters = reactive<MessageListFilters>(createInitialMessageFilters())
const appliedMessageFilters = reactive<MessageListFilters>(createInitialMessageFilters())
const myFilters = reactive<MyMessageFilters>(createInitialMyFilters())
const appliedMyFilters = reactive<MyMessageFilters>(createInitialMyFilters())

const messagePagination = usePagination(
  (params) => fetchMessageList(params, appliedMessageFilters),
  { initialPageSize: 20, pageSizes: [20, 50, 100], immediate: false },
)
const myPagination = usePagination((params) => fetchMyMessageList(params, appliedMyFilters), {
  initialPageSize: 20,
  pageSizes: [20, 50, 100],
})
const { data: managementData, loading: managementLoading } = messagePagination
const { data: inboxData, loading: inboxLoading } = myPagination

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
const formStatusOptions = computed(() => [
  { label: t('message.status.enabled'), value: '1' as const },
  { label: t('message.status.disabled'), value: '0' as const },
])
const readStatusOptions = computed(() => [
  { label: t('message.filter.all'), value: 'all' as const },
  { label: t('message.filter.unread'), value: 'unread' as const },
  { label: t('message.filter.read'), value: 'read' as const },
])
const channelOptions = computed(() => [
  { label: t('message.form.channel.inbox'), value: 'inbox' as const },
  { label: t('message.form.channel.webhook'), value: 'webhook' as const },
  { label: t('message.form.channel.email'), value: 'email' as const },
  { label: t('message.form.channel.sms'), value: 'sms' as const },
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
    componentProps: { clearable: true, options: statusOptions.value },
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

const typeTranslationKeys: Record<MessageType, TranslationKey> = {
  system: 'message.type.system',
  approval: 'message.type.approval',
  alarm: 'message.type.alarm',
}

const getMessageTypeLabel = (messageType: MessageType): string =>
  t(typeTranslationKeys[messageType])

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

const getStatusLabel = (status: MessageStatus): string =>
  status === '1' ? t('message.status.enabled') : t('message.status.disabled')

const getReadStatusLabel = (readAt: string | null): string =>
  readAt ? t('message.read') : t('message.unread')

const formatTimestamp = (value: string | null): string => value ?? t('message.noTime')

const messageColumns = computed<DataTableColumns<MessageListItem>>(() => [
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
    render: (item) =>
      h(
        NTag,
        { type: getMessageTagType(item.message_type), size: 'small', round: true },
        {
          default: () => [
            h(
              NIcon,
              { size: 14, 'aria-hidden': 'true' },
              { default: () => h(getMessageIcon(item.message_type)) },
            ),
            h('span', { class: 'message-type-label' }, getMessageTypeLabel(item.message_type)),
          ],
        },
      ),
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
        ...(canQuery.value
          ? [
              h(
                NButton,
                {
                  quaternary: true,
                  circle: true,
                  'aria-label': t('message.action.detail'),
                  title: t('message.action.detail'),
                  onClick: () => void openManageDetail(item),
                },
                { icon: () => h(NIcon, null, { default: () => h(EyeOutline) }) },
              ),
            ]
          : []),
        ...(canEdit.value
          ? [
              h(
                NButton,
                {
                  quaternary: true,
                  circle: true,
                  'aria-label': t('message.action.edit'),
                  title: t('message.action.edit'),
                  onClick: () => openEditMessage(item),
                },
                { icon: () => h(NIcon, null, { default: () => h(CreateOutline) }) },
              ),
            ]
          : []),
        ...(canDelete.value
          ? [
              h(
                NButton,
                {
                  quaternary: true,
                  circle: true,
                  type: 'error',
                  'aria-label': t('message.action.delete'),
                  title: t('message.action.delete'),
                  onClick: () => confirmDeleteMessage(item),
                },
                { icon: () => h(NIcon, null, { default: () => h(TrashOutline) }) },
              ),
            ]
          : []),
      ]),
  },
])

const myColumns = computed<DataTableColumns<MessageItem>>(() => [
  {
    title: t('message.column.title'),
    key: 'message_title',
    minWidth: 220,
    render: (item) =>
      h(
        'div',
        { class: ['message-inbox-title', { 'message-inbox-title--unread': !item.read_at }] },
        [h('strong', item.message_title)],
      ),
  },
  {
    title: t('message.column.type'),
    key: 'message_type',
    width: 140,
    render: (item) =>
      h(
        NTag,
        { type: getMessageTagType(item.message_type), size: 'small', round: true },
        { default: () => getMessageTypeLabel(item.message_type) },
      ),
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
    width: 110,
    render: (item) =>
      h(
        NButton,
        {
          text: true,
          type: 'primary',
          onClick: () => void openInboxDetail(item),
        },
        { default: () => t('message.action.detail') },
      ),
  },
])

const applyMessageFilters = (nextFilters: MessageListFilters): void => {
  Object.assign(appliedMessageFilters, nextFilters)
}

const applyMyFilters = (nextFilters: MyMessageFilters): void => {
  Object.assign(appliedMyFilters, nextFilters)
}

const handleMessageSearch = async (nextFilters: MessageListFilters): Promise<void> => {
  applyMessageFilters(nextFilters)
  await messagePagination.reset()
}

const handleMySearch = async (nextFilters: MyMessageFilters): Promise<void> => {
  applyMyFilters(nextFilters)
  await myPagination.reset()
}

const refreshCurrentList = async (): Promise<void> => {
  if (viewMode.value === 'manage') {
    await messagePagination.refresh()
    return
  }

  await myPagination.refresh()
}

const createInitialForm = (): MessageFormModel => ({
  message_title: '',
  message_type: 'system',
  message_content: '',
  status: '1',
  publish_time: null,
  recipient_user_ids: '',
  delivery_channels: ['inbox'],
})

const formModel = reactive<MessageFormModel>(createInitialForm())
const formRef = ref<FormInst | null>(null)
const formVisible = ref(false)
const formLoading = ref(false)
const editingMessageId = ref<number | null>(null)
const formMode = ref<'create' | 'edit'>('create')
const formRules = computed<FormRules>(() => ({
  message_title: [
    {
      required: true,
      message: t('message.form.titlePlaceholder'),
      trigger: ['input', 'blur'],
    },
  ],
  message_type: [{ required: true, message: t('message.form.type'), trigger: ['change', 'blur'] }],
  message_content: [
    {
      required: true,
      message: t('message.form.contentPlaceholder'),
      trigger: ['input', 'blur'],
    },
  ],
  delivery_channels: [
    { type: 'array', required: true, message: t('message.form.channels'), trigger: 'change' },
  ],
}))

const detailVisible = ref(false)
const detailLoading = ref(false)
const detailItem = ref<MessageDetailView | null>(null)

const resetForm = (): void => {
  Object.assign(formModel, createInitialForm())
  editingMessageId.value = null
  formMode.value = 'create'
}

const openCreateMessage = (): void => {
  resetForm()
  formVisible.value = true
}

const fillEditForm = (item: MessageListItem): void => {
  Object.assign(formModel, {
    message_title: item.message_title,
    message_type: item.message_type,
    message_content: item.message_content,
    status: item.status,
    publish_time: toMessageFormTime(item.publish_time),
    recipient_user_ids: '',
    delivery_channels: ['inbox'],
  })
  editingMessageId.value = item.id
  formMode.value = 'edit'
}

const openEditMessage = (item: MessageListItem): void => {
  fillEditForm(item)
  formVisible.value = true
}

const saveMessage = async (): Promise<void> => {
  if (formLoading.value) {
    return
  }

  const valid = await formRef.value?.validate()
  if (!valid) {
    return
  }

  let recipientUserIds: number[]
  try {
    recipientUserIds = parseRecipientUserIds(formModel.recipient_user_ids)
  } catch {
    message.error(t('message.form.invalidRecipientIds'))
    return
  }

  formLoading.value = true
  try {
    if (formMode.value === 'edit' && editingMessageId.value !== null) {
      const payload: MessageUpdatePayload = {
        message_title: formModel.message_title.trim(),
        message_type: formModel.message_type,
        message_content: formModel.message_content.trim(),
        status: formModel.status,
        publish_time: toMessagePublishTime(formModel.publish_time),
      }
      await updateMessage(editingMessageId.value, payload)
      message.success(t('message.form.updateSuccess'))
    } else {
      const payload: MessageCreatePayload = {
        message_title: formModel.message_title.trim(),
        message_type: formModel.message_type,
        message_content: formModel.message_content.trim(),
        status: formModel.status,
        publish_time: toMessagePublishTime(formModel.publish_time),
        recipient_user_ids: recipientUserIds,
        delivery_channels: formModel.delivery_channels,
      }
      await createMessage(payload)
      message.success(t('message.form.createSuccess'))
    }

    formVisible.value = false
    await messagePagination.refresh()
    await messageStore.loadLatest()
  } finally {
    formLoading.value = false
  }
}

const confirmDeleteMessage = (item: MessageListItem): void => {
  dialog.warning({
    title: t('message.action.confirmDelete'),
    content: t('message.action.confirmDeleteContent'),
    positiveText: t('message.action.delete'),
    negativeText: t('message.form.cancel'),
    onPositiveClick: async () => {
      await deleteMessage(item.id)
      message.success(t('message.form.deleteSuccess'))
      await messagePagination.refresh()
      await messageStore.loadLatest()
    },
  })
}

const openManageDetail = async (item: MessageListItem): Promise<void> => {
  detailVisible.value = true
  detailLoading.value = true
  detailItem.value = null
  try {
    detailItem.value = await fetchMessageDetail(item.id)
  } finally {
    detailLoading.value = false
  }
}

const openInboxDetail = async (item: MessageItem): Promise<void> => {
  detailVisible.value = true
  detailLoading.value = true
  detailItem.value = null
  try {
    const detail = await fetchMyMessageDetail(item.id)
    if (!detail.read_at) {
      await markMessageRead(item.id)
      messageStore.markLocalRead(item.id)
      detail.read_at = new Date().toISOString()
    }
    detailItem.value = detail
    await myPagination.refresh()
  } finally {
    detailLoading.value = false
  }
}

const markAllInboxRead = async (): Promise<void> => {
  if (!messageStore.hasUnread) {
    return
  }

  const marked = await messageStore.markAllRead()
  if (!marked) {
    return
  }

  message.success(t('message.form.markAllReadSuccess'))
  await myPagination.refresh()
}

const rowKey = (item: MessageListItem | MessageItem): number => item.id
const activeLoading = computed(() =>
  viewMode.value === 'manage' ? messagePagination.loading.value : myPagination.loading.value,
)
const activeError = computed(() =>
  viewMode.value === 'manage' ? messagePagination.error.value : myPagination.error.value,
)
const activePaginationBinding = computed(() =>
  viewMode.value === 'manage' ? messagePagination.pagination.value : myPagination.pagination.value,
)
const totalLabel = computed(() =>
  t('message.total').replace(
    '{count}',
    String(viewMode.value === 'manage' ? messagePagination.total.value : myPagination.total.value),
  ),
)
const pageInfo = computed(() =>
  t('message.pageInfo')
    .replace(
      '{page}',
      String(viewMode.value === 'manage' ? messagePagination.page.value : myPagination.page.value),
    )
    .replace(
      '{pageSize}',
      String(
        viewMode.value === 'manage'
          ? messagePagination.pageSize.value
          : myPagination.pageSize.value,
      ),
    ),
)

watch(viewMode, (nextMode) => {
  if (nextMode === 'manage' && canManage.value && messagePagination.data.value.length === 0) {
    void messagePagination.load()
  }
})

onMounted(() => {
  const messageId = Number(route.query.messageId)
  if (Number.isInteger(messageId) && messageId > 0) {
    void openInboxDetail({
      id: messageId,
      message_title: '',
      message_type: 'system',
      message_content: '',
      publish_time: null,
      read_at: null,
    })
  }
})
</script>

<template>
  <main class="message-page">
    <header class="message-page-header">
      <div class="message-page-heading">
        <div class="message-page-eyebrow">
          <NIcon :size="16" aria-hidden="true"><NotificationsOutline /></NIcon>
          <span>{{ t('message.title') }}</span>
        </div>
        <h1>{{ t('message.title') }}</h1>
        <p>{{ t('message.description') }}</p>
      </div>
      <div class="message-page-actions">
        <NRadioGroup v-model:value="viewMode" name="message-view-mode" size="small">
          <NRadioButton value="inbox">{{ t('message.mode.inbox') }}</NRadioButton>
          <NRadioButton v-if="canManage" value="manage">{{
            t('message.mode.manage')
          }}</NRadioButton>
        </NRadioGroup>
        <NButton
          v-if="viewMode === 'inbox'"
          quaternary
          :disabled="!messageStore.hasUnread || inboxLoading"
          @click="markAllInboxRead"
        >
          <template #icon>
            <NIcon><CheckmarkDoneOutline /></NIcon>
          </template>
          {{ t('message.action.markAllRead') }}
        </NButton>
        <NButton
          v-if="viewMode === 'manage' && canCreate"
          type="primary"
          @click="openCreateMessage"
        >
          <template #icon>
            <NIcon><AddOutline /></NIcon>
          </template>
          {{ t('message.action.create') }}
        </NButton>
        <NButton
          quaternary
          circle
          :loading="activeLoading"
          :aria-label="t('message.refresh')"
          :title="t('message.refresh')"
          @click="refreshCurrentList"
        >
          <template #icon>
            <NIcon><RefreshOutline /></NIcon>
          </template>
        </NButton>
      </div>
    </header>

    <section class="message-list-panel" :aria-labelledby="`${viewMode}-message-list-title`">
      <div class="message-list-heading">
        <div>
          <h2 :id="`${viewMode}-message-list-title`">
            {{ viewMode === 'manage' ? t('message.manageTitle') : t('message.inboxTitle') }}
          </h2>
          <p>
            {{
              viewMode === 'manage' ? t('message.manageDescription') : t('message.inboxDescription')
            }}
          </p>
        </div>
        <span>{{ totalLabel }}</span>
      </div>

      <AppSearchForm
        v-if="viewMode === 'manage'"
        :model="messageFilters"
        :initial-values="createInitialMessageFilters()"
        :fields="messageSearchFields"
        :loading="managementLoading"
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
        @search="handleMessageSearch"
        @reset="handleMessageSearch"
      />

      <AppSearchForm
        v-else
        :model="myFilters"
        :initial-values="createInitialMyFilters()"
        :fields="mySearchFields"
        :loading="inboxLoading"
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
        @search="handleMySearch"
        @reset="handleMySearch"
      />

      <div v-if="activeError" class="message-page-error">
        <NAlert type="error" :show-icon="false">{{ t('message.loadFailed') }}</NAlert>
        <NButton size="small" @click="refreshCurrentList">{{ t('message.retry') }}</NButton>
      </div>

      <NDataTable
        v-if="viewMode === 'manage'"
        :columns="messageColumns"
        :data="managementData"
        :loading="managementLoading"
        remote
        :row-key="rowKey"
        :scroll-x="1120"
      >
        <template #empty><NEmpty :description="t('message.empty')" /></template>
      </NDataTable>

      <NDataTable
        v-else
        :columns="myColumns"
        :data="inboxData"
        :loading="inboxLoading"
        remote
        :row-key="rowKey"
        :scroll-x="1080"
      >
        <template #empty><NEmpty :description="t('message.empty')" /></template>
      </NDataTable>

      <footer class="message-page-footer">
        <NPagination v-bind="activePaginationBinding" />
        <span>{{ pageInfo }}</span>
      </footer>
    </section>

    <NModal
      v-model:show="detailVisible"
      preset="card"
      class="message-modal message-detail-modal"
      :title="t('message.detailTitle')"
    >
      <NSpin :show="detailLoading">
        <NEmpty v-if="!detailItem && !detailLoading" :description="t('message.empty')" />
        <div v-else-if="detailItem" class="message-detail">
          <header class="message-detail-heading">
            <span
              class="message-detail-icon"
              :class="`message-detail-icon--${getMessageTagType(detailItem.message_type)}`"
              aria-hidden="true"
            >
              <NIcon :size="20"><component :is="getMessageIcon(detailItem.message_type)" /></NIcon>
            </span>
            <div class="message-detail-title">
              <NTag
                class="message-detail-type"
                :type="getMessageTagType(detailItem.message_type)"
                size="small"
                round
              >
                {{ getMessageTypeLabel(detailItem.message_type) }}
              </NTag>
              <h3>{{ detailItem.message_title }}</h3>
            </div>
          </header>
          <section class="message-detail-content-section">
            <span class="message-detail-content-label">{{ t('message.column.content') }}</span>
            <p class="message-detail-content">{{ detailItem.message_content }}</p>
          </section>
          <NDivider />
          <dl class="message-detail-meta">
            <div>
              <dt>{{ t('message.column.publishTime') }}</dt>
              <dd>{{ formatTimestamp(detailItem.publish_time) }}</dd>
            </div>
            <div v-if="'status' in detailItem">
              <dt>{{ t('message.column.status') }}</dt>
              <dd>{{ getStatusLabel(detailItem.status) }}</dd>
            </div>
            <div v-if="'read_at' in detailItem">
              <dt>{{ t('message.column.readStatus') }}</dt>
              <dd>{{ getReadStatusLabel(detailItem.read_at) }}</dd>
            </div>
          </dl>
        </div>
      </NSpin>
    </NModal>

    <NModal
      v-model:show="formVisible"
      preset="card"
      class="message-modal"
      :title="formMode === 'create' ? t('message.createTitle') : t('message.editTitle')"
      :mask-closable="false"
      @after-leave="resetForm"
    >
      <NForm ref="formRef" :model="formModel" :rules="formRules" label-placement="top">
        <div class="message-form-grid">
          <NFormItem :label="t('message.form.title')" path="message_title">
            <NInput
              v-model:value="formModel.message_title"
              :placeholder="t('message.form.titlePlaceholder')"
            />
          </NFormItem>
          <NFormItem :label="t('message.form.type')" path="message_type">
            <NSelect
              v-model:value="formModel.message_type"
              :options="messageTypeOptions"
              :placeholder="t('message.form.typePlaceholder')"
            />
          </NFormItem>
          <NFormItem :label="t('message.form.status')" path="status">
            <NSelect v-model:value="formModel.status" :options="formStatusOptions" />
          </NFormItem>
          <NFormItem :label="t('message.form.publishTime')" path="publish_time">
            <NDatePicker
              v-model:value="formModel.publish_time"
              type="datetime"
              clearable
              class="message-form-control"
            />
          </NFormItem>
        </div>
        <NFormItem :label="t('message.form.content')" path="message_content">
          <NInput
            v-model:value="formModel.message_content"
            type="textarea"
            :rows="6"
            :placeholder="t('message.form.contentPlaceholder')"
          />
        </NFormItem>
        <NFormItem
          v-if="formMode === 'create'"
          :label="t('message.form.recipientIds')"
          path="recipient_user_ids"
        >
          <NInput
            v-model:value="formModel.recipient_user_ids"
            :placeholder="t('message.form.recipientIdsPlaceholder')"
          />
          <template #feedback>{{ t('message.form.recipientIdsHelp') }}</template>
        </NFormItem>
        <NFormItem
          v-if="formMode === 'create'"
          :label="t('message.form.channels')"
          path="delivery_channels"
        >
          <NSelect v-model:value="formModel.delivery_channels" multiple :options="channelOptions" />
        </NFormItem>
        <div class="message-modal-actions">
          <NButton :disabled="formLoading" @click="formVisible = false">{{
            t('message.form.cancel')
          }}</NButton>
          <NButton type="primary" :loading="formLoading" @click="saveMessage">
            <template #icon
              ><NIcon><CheckmarkDoneOutline /></NIcon
            ></template>
            {{ t('message.form.save') }}
          </NButton>
        </div>
      </NForm>
    </NModal>
  </main>
</template>

<style scoped>
.message-page {
  display: grid;
  gap: 16px;
  min-width: 0;
  color: var(--app-color-text);
}

.message-page-header,
.message-list-heading,
.message-page-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.message-page-heading,
.message-list-heading > div {
  min-width: 0;
}

.message-page-eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
  color: var(--app-color-primary);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.message-page-heading h1,
.message-page-heading p,
.message-list-heading h2,
.message-list-heading p,
.message-list-heading span {
  margin: 0;
}

.message-page-heading h1 {
  font-size: 24px;
  line-height: 1.3;
}

.message-page-heading p,
.message-list-heading p {
  margin-top: 6px;
  color: var(--app-color-text-muted);
  font-size: 13px;
  line-height: 1.5;
}

.message-page-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  flex-wrap: wrap;
}

.message-list-panel {
  min-width: 0;
  padding: 20px 24px 0;
  overflow: hidden;
  border: 1px solid var(--app-color-border);
  border-radius: 8px;
  background: var(--app-color-surface);
}

.message-list-heading {
  align-items: flex-start;
  margin-bottom: 16px;
}

.message-list-heading h2 {
  font-size: 16px;
}

.message-list-heading > span,
.message-page-footer span {
  flex: 0 0 auto;
  color: var(--app-color-text-muted);
  font-size: 13px;
}

.message-list-panel :deep(.n-data-table) {
  margin: 0 -24px;
}

.message-page-error {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 16px 0;
}

.message-page-error .n-alert {
  flex: 1;
}

.message-page-footer {
  min-height: 64px;
  padding: 12px 0;
  border-top: 1px solid var(--app-color-border);
}

.message-type-label {
  margin-left: 4px;
}

.message-row-actions {
  display: flex;
  align-items: center;
  gap: 2px;
}

.message-inbox-title {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.message-inbox-title--unread::before {
  width: 6px;
  height: 6px;
  flex: 0 0 6px;
  border-radius: 50%;
  background: var(--app-color-primary);
  content: '';
}

.message-detail {
  min-width: 0;
}

.message-detail-heading {
  display: flex;
  align-items: flex-start;
  gap: 14px;
}

.message-detail-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 42px;
  height: 42px;
  flex: 0 0 42px;
  border-radius: 10px;
  background: var(--app-color-fill);
}

.message-detail-icon--info {
  color: var(--app-color-primary);
}

.message-detail-icon--warning {
  color: var(--app-color-warning);
}

.message-detail-icon--error {
  color: var(--app-color-danger);
}

.message-detail-title {
  display: grid;
  min-width: 0;
  gap: 8px;
}

.message-detail-type {
  justify-self: start;
}

.message-detail-heading h3 {
  min-width: 0;
  margin: 0;
  overflow-wrap: anywhere;
  font-size: 20px;
  line-height: 1.4;
}

.message-detail-content-section {
  margin-top: 24px;
  padding: 16px 18px;
  border-left: 3px solid var(--app-color-primary);
  border-radius: 4px;
  background: var(--app-color-fill);
}

.message-detail-content-label {
  display: block;
  color: var(--app-color-text-muted);
  font-size: 12px;
  font-weight: 600;
}

.message-detail-content {
  margin: 8px 0 0;
  color: var(--app-color-text);
  line-height: 1.8;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}

.message-detail-meta {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0 24px;
  margin: 0;
}

.message-detail-meta div {
  min-width: 0;
  padding: 12px 0;
  border-bottom: 1px solid var(--app-color-border);
}

.message-detail-meta dt {
  color: var(--app-color-text-muted);
  font-size: 12px;
}

.message-detail-meta dd {
  margin: 4px 0 0;
  color: var(--app-color-text);
  overflow-wrap: anywhere;
}

.message-form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0 16px;
}

.message-form-control {
  width: 100%;
}

.message-modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  padding-top: 8px;
}

@media (width <= 720px) {
  .message-page-header,
  .message-list-heading {
    align-items: stretch;
    flex-direction: column;
  }

  .message-page-actions {
    justify-content: flex-start;
  }
}

@media (width <= 640px) {
  .message-list-panel {
    padding-right: 16px;
    padding-left: 16px;
  }

  .message-list-panel :deep(.n-data-table) {
    margin: 0 -16px;
  }

  .message-page-footer {
    align-items: flex-start;
    flex-direction: column-reverse;
  }
}

@media (width <= 520px) {
  .message-detail-meta {
    grid-template-columns: 1fr;
  }

  .message-form-grid {
    grid-template-columns: 1fr;
  }
}
</style>

<style>
.n-card.message-modal {
  width: min(760px, calc(100vw - 32px));
}

.n-card.message-detail-modal {
  width: min(640px, calc(100vw - 32px));
}
</style>
