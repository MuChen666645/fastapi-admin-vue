<script setup lang="ts">
import { AlertCircleOutline, ClipboardOutline, InformationCircleOutline } from '@vicons/ionicons5'
import { NDivider, NEmpty, NIcon, NModal, NSpin, NTag } from 'naive-ui'

import { useLocale } from '@/hooks'
import type { MessageDetailView, MessageStatus, MessageType, TranslationKey } from '@/types'
import { resolveMessageTone } from '@/utils'

defineOptions({ name: 'MessageDetailModal' })

interface MessageDetailModalProps {
  show: boolean
  loading: boolean
  item: MessageDetailView | null
}

const props = defineProps<MessageDetailModalProps>()

const emit = defineEmits<{
  'update:show': [value: boolean]
}>()

const { t } = useLocale()

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
</script>

<template>
  <NModal
    :show="props.show"
    preset="card"
    class="message-modal message-detail-modal"
    :title="t('message.detailTitle')"
    @update:show="emit('update:show', $event)"
  >
    <NSpin :show="props.loading">
      <NEmpty v-if="!props.item && !props.loading" :description="t('message.empty')" />
      <div v-else-if="props.item" class="message-detail">
        <header class="message-detail-heading">
          <span
            class="message-detail-icon"
            :class="`message-detail-icon--${getMessageTagType(props.item.message_type)}`"
            aria-hidden="true"
          >
            <NIcon :size="20"><component :is="getMessageIcon(props.item.message_type)" /></NIcon>
          </span>
          <div class="message-detail-title">
            <NTag
              class="message-detail-type"
              :type="getMessageTagType(props.item.message_type)"
              size="small"
              round
            >
              {{ getMessageTypeLabel(props.item.message_type) }}
            </NTag>
            <h3>{{ props.item.message_title }}</h3>
          </div>
        </header>
        <section class="message-detail-content-section">
          <span class="message-detail-content-label">{{ t('message.column.content') }}</span>
          <p class="message-detail-content">{{ props.item.message_content }}</p>
        </section>
        <NDivider />
        <dl class="message-detail-meta">
          <div>
            <dt>{{ t('message.column.publishTime') }}</dt>
            <dd>{{ formatTimestamp(props.item.publish_time) }}</dd>
          </div>
          <div v-if="'status' in props.item">
            <dt>{{ t('message.column.status') }}</dt>
            <dd>{{ getStatusLabel(props.item.status) }}</dd>
          </div>
          <div v-if="'read_at' in props.item">
            <dt>{{ t('message.column.readStatus') }}</dt>
            <dd>{{ getReadStatusLabel(props.item.read_at) }}</dd>
          </div>
        </dl>
      </div>
    </NSpin>
  </NModal>
</template>

<style lang="scss" scoped>
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

@media (width <= 520px) {
  .message-detail-meta {
    grid-template-columns: 1fr;
  }
}
</style>

<style lang="scss">
.n-card.message-detail-modal {
  width: min(640px, calc(100vw - 32px));
}
</style>
