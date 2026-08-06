<script setup lang="ts">
import { computed } from 'vue'
import {
  AlertCircleOutline,
  ClipboardOutline,
  InformationCircleOutline,
  RefreshOutline,
} from '@vicons/ionicons5'
import { NAlert, NButton, NEmpty, NIcon, NSpin } from 'naive-ui'

import { useLocale } from '@/hooks'
import { formatMessageRelativeTime, resolveMessageTone } from '@/utils'
import type { MessageItem, MessageTab } from '@/types'

defineOptions({ name: 'MessageCenter' })

const props = withDefaults(
  defineProps<{
    activeTab: MessageTab
    compact?: boolean
    error: Error | null
    items: MessageItem[]
    loading: boolean
    showFooter?: boolean
    tabUnreadCounts: Record<MessageTab, number>
  }>(),
  { compact: false, showFooter: false },
)

const emit = defineEmits<{
  refresh: []
  select: [item: MessageItem]
  'update:activeTab': [tab: MessageTab]
  viewAll: []
}>()

const { language, t } = useLocale()

const formatTime = (value: string | null): string =>
  formatMessageRelativeTime(value, language.value)

const tabs = computed<ReadonlyArray<{ key: MessageTab; label: string }>>(() => [
  { key: 'system', label: t('message.type.system') },
  { key: 'approval', label: t('message.type.approval') },
  { key: 'alarm', label: t('message.type.alarm') },
])

const iconByTone = {
  danger: AlertCircleOutline,
  warning: ClipboardOutline,
  info: InformationCircleOutline,
} as const

const getItemIcon = (item: MessageItem) => iconByTone[resolveMessageTone(item.message_type)]

const selectTab = (tab: MessageTab): void => {
  emit('update:activeTab', tab)
}

const selectItem = (item: MessageItem): void => {
  emit('select', item)
}
</script>

<template>
  <section class="message-center" :class="{ 'message-center--compact': props.compact }">
    <nav class="message-tabs" :aria-label="t('message.tabs')">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        type="button"
        class="message-tab"
        :class="{ 'message-tab--active': props.activeTab === tab.key }"
        :aria-selected="props.activeTab === tab.key"
        role="tab"
        @click="selectTab(tab.key)"
      >
        <span>{{ tab.label }}</span>
        <span v-if="props.tabUnreadCounts[tab.key] > 0" class="message-tab-count">
          {{ props.tabUnreadCounts[tab.key] }}
        </span>
      </button>
    </nav>

    <div v-if="props.error" class="message-error">
      <NAlert type="error" :show-icon="false">
        {{ t('message.loadFailed') }}
      </NAlert>
      <NButton size="small" secondary @click="emit('refresh')">
        {{ t('message.retry') }}
      </NButton>
    </div>

    <div v-else class="message-list" role="tabpanel">
      <NSpin :show="props.loading">
        <button
          v-for="item in props.items"
          :key="item.id"
          type="button"
          class="message-item"
          :class="{ 'message-item--unread': !item.read_at }"
          :title="item.message_title"
          @click="selectItem(item)"
        >
          <span
            class="message-item-icon"
            :class="`message-item-icon--${resolveMessageTone(item.message_type)}`"
            aria-hidden="true"
          >
            <NIcon :size="props.compact ? 15 : 18"><component :is="getItemIcon(item)" /></NIcon>
          </span>
          <span class="message-item-copy">
            <strong>{{ item.message_title }}</strong>
            <span v-if="!props.compact" class="message-item-content">
              {{ item.message_content }}
            </span>
            <time>{{ formatTime(item.publish_time) || t('message.noTime') }}</time>
          </span>
          <span v-if="!item.read_at" class="message-item-dot" :aria-label="t('message.unread')" />
        </button>

        <NEmpty
          v-if="props.items.length === 0 && !props.loading"
          class="message-empty"
          :description="t('message.empty')"
        />
      </NSpin>
    </div>

    <div v-if="props.showFooter" class="message-footer">
      <NButton text type="primary" @click="emit('viewAll')">
        {{ t('message.viewAll') }}
      </NButton>
      <NButton
        quaternary
        circle
        :loading="props.loading"
        :aria-label="t('message.refresh')"
        :title="t('message.refresh')"
        @click="emit('refresh')"
      >
        <template #icon>
          <NIcon><RefreshOutline /></NIcon>
        </template>
      </NButton>
    </div>
  </section>
</template>

<style lang="scss" scoped>
.message-center {
  min-width: 0;
  overflow: hidden;
  color: var(--app-color-text);
  background: var(--app-color-surface);
}

.message-tabs {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  height: 52px;
  border-bottom: 1px solid var(--app-color-border);
}

.message-tab {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  min-width: 0;
  padding: 0 8px;
  color: var(--app-color-text-muted);
  border: 0;
  background: transparent;
  cursor: pointer;
  font: inherit;
  font-size: 13px;
}

.message-tab:hover,
.message-tab:focus-visible {
  color: var(--app-color-primary);
  outline: none;
}

.message-tab--active {
  color: var(--app-color-primary);
  font-weight: 700;
}

.message-tab--active::after {
  position: absolute;
  right: 20%;
  bottom: -1px;
  left: 20%;
  height: 2px;
  content: '';
  background: var(--app-color-primary);
}

.message-tab-count {
  color: inherit;
  font-size: 11px;
}

.message-list {
  min-height: 80px;
}

.message-list :deep(.n-spin-container) {
  min-height: inherit;
}

.message-item {
  display: flex;
  width: 100%;
  align-items: center;
  gap: 12px;
  min-height: 72px;
  padding: 12px 16px;
  text-align: left;
  border: 0;
  border-bottom: 1px solid var(--app-color-border);
  background: var(--app-color-surface);
  cursor: pointer;
  font: inherit;
}

.message-item:hover,
.message-item:focus-visible {
  background: var(--app-color-primary-soft);
  outline: none;
}

.message-item--unread {
  background: color-mix(in srgb, var(--app-color-primary-soft) 38%, var(--app-color-surface));
}

.message-item-icon {
  display: grid;
  width: 32px;
  height: 32px;
  flex: 0 0 32px;
  place-items: center;
  border-radius: 50%;
}

.message-item-icon--danger {
  color: var(--app-color-danger);
  background: var(--app-color-danger-soft);
}

.message-item-icon--warning {
  color: var(--app-color-warning);
  background: var(--app-color-warning-soft);
}

.message-item-icon--info {
  color: var(--app-color-primary);
  background: var(--app-color-primary-soft);
}

.message-item-copy {
  display: grid;
  min-width: 0;
  flex: 1;
  gap: 4px;
}

.message-item-copy strong,
.message-item-content,
.message-item-copy time {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.message-item-copy strong {
  color: var(--app-color-text);
  font-size: 13px;
  font-weight: 600;
}

.message-item-content,
.message-item-copy time {
  color: var(--app-color-text-muted);
  font-size: 12px;
  line-height: 1.4;
}

.message-item-copy time {
  font-size: 11px;
}

.message-item-dot {
  width: 6px;
  height: 6px;
  flex: 0 0 6px;
  border-radius: 50%;
  background: var(--app-color-primary);
}

.message-empty {
  padding: 28px 16px;
}

.message-error {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px;
}

.message-error .n-alert {
  min-width: 0;
  flex: 1;
}

.message-footer {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 52px;
  padding: 8px 12px;
  border-top: 1px solid var(--app-color-border);
}

.message-footer .n-button:last-child {
  position: absolute;
  right: 12px;
}

.message-center:not(.message-center--compact) .message-item {
  align-items: flex-start;
  min-height: 86px;
  padding: 16px 20px;
}

@media (width <= 560px) {
  .message-item {
    padding-right: 12px;
    padding-left: 12px;
  }

  .message-center:not(.message-center--compact) .message-item {
    padding-right: 16px;
    padding-left: 16px;
  }
}
</style>
