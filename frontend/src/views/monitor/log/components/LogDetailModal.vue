<script setup lang="ts">
import { computed } from 'vue'
import { NDescriptions, NDescriptionsItem, NEmpty, NModal, NTag } from 'naive-ui'

import { useLocale } from '@/hooks'
import type { ExceptionLogItem, LoginLogItem, LogDetailModalProps, OperationLogItem } from '@/types'
import { formatDateTime } from '@/utils'

defineOptions({ name: 'LogDetailModal' })

const props = defineProps<LogDetailModalProps>()
const emit = defineEmits<{ 'update:show': [value: boolean] }>()
const { t } = useLocale()

const loginItem = computed<LoginLogItem | null>(() =>
  props.kind === 'login' && props.item !== null && 'login_time' in props.item ? props.item : null,
)
const operationItem = computed<OperationLogItem | null>(() =>
  props.kind === 'operation' && props.item !== null && 'operation_time' in props.item
    ? props.item
    : null,
)
const exceptionItem = computed<ExceptionLogItem | null>(() =>
  props.kind === 'exception' && props.item !== null && 'exception_time' in props.item
    ? props.item
    : null,
)

const displayValue = (value: string | number | null): string =>
  value === null || value === '' ? t('log.noValue') : String(value)
</script>

<template>
  <NModal
    :show="props.show"
    preset="card"
    class="log-detail-modal"
    :title="t('log.detailTitle')"
    @update:show="emit('update:show', $event)"
  >
    <NEmpty v-if="!props.item" :description="t('log.empty')" />
    <NDescriptions v-else-if="loginItem" bordered :column="2" label-placement="left" size="small">
      <NDescriptionsItem :label="t('log.column.username')">
        {{ loginItem.username }}
      </NDescriptionsItem>
      <NDescriptionsItem :label="t('log.column.status')">
        <NTag :type="loginItem.status === '1' ? 'success' : 'error'" size="small">
          {{ loginItem.status === '1' ? t('log.status.success') : t('log.status.failed') }}
        </NTag>
      </NDescriptionsItem>
      <NDescriptionsItem :label="t('log.column.userId')">
        {{ displayValue(loginItem.user_id) }}
      </NDescriptionsItem>
      <NDescriptionsItem :label="t('log.column.ipAddress')">
        {{ displayValue(loginItem.ip_address) }}
      </NDescriptionsItem>
      <NDescriptionsItem :label="t('log.column.message')" :span="2">
        {{ displayValue(loginItem.message) }}
      </NDescriptionsItem>
      <NDescriptionsItem :label="t('log.column.userAgent')" :span="2">
        {{ displayValue(loginItem.user_agent) }}
      </NDescriptionsItem>
      <NDescriptionsItem :label="t('log.column.time')" :span="2">
        {{ formatDateTime(loginItem.login_time, { fallback: t('log.noValue') }) }}
      </NDescriptionsItem>
    </NDescriptions>
    <NDescriptions
      v-else-if="operationItem"
      bordered
      :column="2"
      label-placement="left"
      size="small"
    >
      <NDescriptionsItem :label="t('log.column.username')">
        {{ displayValue(operationItem.username) }}
      </NDescriptionsItem>
      <NDescriptionsItem :label="t('log.column.userId')">
        {{ displayValue(operationItem.user_id) }}
      </NDescriptionsItem>
      <NDescriptionsItem :label="t('log.column.method')">
        {{ operationItem.method }}
      </NDescriptionsItem>
      <NDescriptionsItem :label="t('log.column.statusCode')">
        {{ operationItem.status_code }}
      </NDescriptionsItem>
      <NDescriptionsItem :label="t('log.column.path')" :span="2">
        {{ operationItem.path }}
      </NDescriptionsItem>
      <NDescriptionsItem :label="t('log.column.ipAddress')">
        {{ displayValue(operationItem.ip_address) }}
      </NDescriptionsItem>
      <NDescriptionsItem :label="t('log.column.duration')">
        {{ t('log.duration').replace('{value}', String(operationItem.duration_ms)) }}
      </NDescriptionsItem>
      <NDescriptionsItem :label="t('log.column.userAgent')" :span="2">
        {{ displayValue(operationItem.user_agent) }}
      </NDescriptionsItem>
      <NDescriptionsItem :label="t('log.column.time')" :span="2">
        {{ formatDateTime(operationItem.operation_time, { fallback: t('log.noValue') }) }}
      </NDescriptionsItem>
    </NDescriptions>
    <NDescriptions
      v-else-if="exceptionItem"
      bordered
      :column="2"
      label-placement="left"
      size="small"
    >
      <NDescriptionsItem :label="t('log.column.username')">
        {{ displayValue(exceptionItem.username) }}
      </NDescriptionsItem>
      <NDescriptionsItem :label="t('log.column.userId')">
        {{ displayValue(exceptionItem.user_id) }}
      </NDescriptionsItem>
      <NDescriptionsItem :label="t('log.column.method')">
        {{ exceptionItem.method }}
      </NDescriptionsItem>
      <NDescriptionsItem :label="t('log.column.ipAddress')">
        {{ displayValue(exceptionItem.ip_address) }}
      </NDescriptionsItem>
      <NDescriptionsItem :label="t('log.column.path')" :span="2">
        {{ exceptionItem.path }}
      </NDescriptionsItem>
      <NDescriptionsItem :label="t('log.column.exceptionType')" :span="2">
        {{ exceptionItem.exception_type }}
      </NDescriptionsItem>
      <NDescriptionsItem :label="t('log.column.message')" :span="2">
        {{ exceptionItem.exception_message }}
      </NDescriptionsItem>
      <NDescriptionsItem :label="t('log.column.traceback')" :span="2">
        <pre class="log-traceback">{{ displayValue(exceptionItem.traceback) }}</pre>
      </NDescriptionsItem>
      <NDescriptionsItem :label="t('log.column.time')" :span="2">
        {{ formatDateTime(exceptionItem.exception_time, { fallback: t('log.noValue') }) }}
      </NDescriptionsItem>
    </NDescriptions>
  </NModal>
</template>

<style lang="scss">
.n-card.log-detail-modal {
  width: min(840px, calc(100vw - 32px));
}

.log-traceback {
  max-height: 320px;
  margin: 0;
  overflow: auto;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  font-family: var(--app-font-family-mono, monospace);
  font-size: 12px;
  line-height: 1.5;
}
</style>
