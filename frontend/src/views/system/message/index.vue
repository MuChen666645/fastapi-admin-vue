<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { AddOutline, CheckmarkDoneOutline, RefreshOutline } from '@vicons/ionicons5'
import {
  NAlert,
  NButton,
  NIcon,
  NPagination,
  NRadioButton,
  NRadioGroup,
  useDialog,
  useMessage,
} from 'naive-ui'
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
import { useLocale, usePagination } from '@/hooks'
import { useMessageStore } from '@/stores'
import MessageDetailModal from './components/MessageDetailModal.vue'
import MessageFormModal from './components/MessageFormModal.vue'
import MessageSearchPanel from './components/MessageSearchPanel.vue'
import MessageTable from './components/MessageTable.vue'
import type {
  MessageCreatePayload,
  MessageDetailView,
  MessageFormMode,
  MessageFormModel,
  MessageItem,
  MessageListFilters,
  MessageListItem,
  MessageUpdatePayload,
  MessageViewMode,
  MyMessageFilters,
} from '@/types'
import { parseRecipientUserIds, toMessageFormTime, toMessagePublishTime } from '@/utils'

defineOptions({ name: 'SystemMessageView' })

const route = useRoute()
const messageStore = useMessageStore()
const dialog = useDialog()
const message = useMessage()
const { t } = useLocale()

const viewMode = ref<MessageViewMode>('inbox')

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

  await Promise.all([myPagination.refresh(), messageStore.loadLatest()])
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
const formVisible = ref(false)
const formLoading = ref(false)
const editingMessageId = ref<number | null>(null)
const formMode = ref<MessageFormMode>('create')

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

const saveMessage = async (model: MessageFormModel): Promise<void> => {
  if (formLoading.value) {
    return
  }

  let recipientUserIds: number[]
  try {
    recipientUserIds = parseRecipientUserIds(model.recipient_user_ids)
  } catch {
    message.error(t('message.form.invalidRecipientIds'))
    return
  }

  formLoading.value = true
  try {
    if (formMode.value === 'edit') {
      if (editingMessageId.value === null) {
        return
      }

      const payload: MessageUpdatePayload = {
        message_title: model.message_title.trim(),
        message_type: model.message_type,
        message_content: model.message_content.trim(),
        status: model.status,
        publish_time: toMessagePublishTime(model.publish_time),
      }
      await updateMessage(editingMessageId.value, payload)
      message.success(t('message.form.updateSuccess'))
    } else {
      const payload: MessageCreatePayload = {
        message_title: model.message_title.trim(),
        message_type: model.message_type,
        message_content: model.message_content.trim(),
        status: model.status,
        publish_time: toMessagePublishTime(model.publish_time),
        recipient_user_ids: recipientUserIds,
        delivery_channels: model.delivery_channels,
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
  if (nextMode === 'manage' && messagePagination.data.value.length === 0) {
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

  if (!messageStore.latestLoaded && !messageStore.latestLoading) {
    void messageStore.loadLatest()
  }
})
</script>

<template>
  <main class="message-page">
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
        <div class="message-page-actions">
          <NRadioGroup v-model:value="viewMode" name="message-view-mode" size="medium">
            <NRadioButton value="inbox">{{ t('message.mode.inbox') }}</NRadioButton>
            <NRadioButton v-permission="'system:message:list'" value="manage">{{
              t('message.mode.manage')
            }}</NRadioButton>
          </NRadioGroup>
          <NButton
            v-if="viewMode === 'inbox'"
            type="primary"
            size="medium"
            :loading="messageStore.latestLoading"
            :disabled="messageStore.latestLoading || !messageStore.hasUnread || inboxLoading"
            @click="markAllInboxRead"
          >
            <template #icon>
              <NIcon><CheckmarkDoneOutline /></NIcon>
            </template>
            {{ t('message.action.markAllRead') }}
          </NButton>
          <NButton
            v-if="viewMode === 'manage'"
            v-permission="'system:message:add'"
            type="primary"
            size="medium"
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
            size="medium"
            :loading="activeLoading"
            :aria-label="t('message.refresh')"
            :title="t('message.refresh')"
            @click="refreshCurrentList"
          >
            <template #icon>
              <NIcon><RefreshOutline /></NIcon>
            </template>
          </NButton>
          <span class="message-total">{{ totalLabel }}</span>
        </div>
      </div>

      <MessageSearchPanel
        :mode="viewMode"
        :management-model="messageFilters"
        :management-initial-values="createInitialMessageFilters()"
        :inbox-model="myFilters"
        :inbox-initial-values="createInitialMyFilters()"
        :management-loading="managementLoading"
        :inbox-loading="inboxLoading"
        @manage-search="handleMessageSearch"
        @inbox-search="handleMySearch"
      />

      <div v-if="activeError" class="message-page-error">
        <NAlert type="error" :show-icon="false">{{ t('message.loadFailed') }}</NAlert>
        <NButton size="small" @click="refreshCurrentList">
          {{ t('message.retry') }}
        </NButton>
      </div>

      <MessageTable
        :mode="viewMode"
        :management-data="managementData"
        :inbox-data="inboxData"
        :management-loading="managementLoading"
        :inbox-loading="inboxLoading"
        @manage-detail="openManageDetail"
        @edit="openEditMessage"
        @delete="confirmDeleteMessage"
        @inbox-detail="openInboxDetail"
      />

      <footer class="message-page-footer">
        <NPagination v-bind="activePaginationBinding" />
        <span>{{ pageInfo }}</span>
      </footer>
    </section>

    <MessageDetailModal v-model:show="detailVisible" :loading="detailLoading" :item="detailItem" />

    <MessageFormModal
      v-model:show="formVisible"
      :mode="formMode"
      :model="formModel"
      :loading="formLoading"
      @submit="saveMessage"
      @reset="resetForm"
    />
  </main>
</template>

<style lang="scss" scoped>
.message-page {
  display: grid;
  gap: 16px;
  min-width: 0;
  color: var(--app-color-text);
}

.message-list-heading,
.message-page-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.message-list-heading > div {
  min-width: 0;
}

.message-list-heading h2,
.message-list-heading p,
.message-total {
  margin: 0;
}
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

.message-total,
.message-page-footer span {
  flex: 0 0 auto;
  color: var(--app-color-text-muted);
  font-size: 13px;
}

.message-list-panel :deep(.n-data-table) {
  margin: 16px 0;
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

@media (width <= 720px) {
  .message-list-heading {
    align-items: stretch;
    flex-direction: column;
  }

  .message-page-actions {
    justify-content: flex-start;
    flex-wrap: wrap;
  }
}

@media (width <= 640px) {
  .message-list-panel {
    padding-right: 16px;
    padding-left: 16px;
  }

  .message-list-panel :deep(.n-data-table) {
    margin: 16px -16px 0;
  }

  .message-page-footer {
    align-items: flex-start;
    flex-direction: column-reverse;
  }
}
</style>
