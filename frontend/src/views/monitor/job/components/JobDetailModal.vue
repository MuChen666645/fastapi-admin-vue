<script setup lang="ts">
import { NDescriptions, NDescriptionsItem, NEmpty, NModal, NSpin, NTag } from 'naive-ui'

import { useLocale } from '@/hooks'
import type { ScheduledJobDetailModalProps } from '@/types'
import { formatDateTime } from '@/utils'
import { getJobExecutionStatusLabel, getJobExecutionStatusTone } from '../presentation'

defineOptions({ name: 'JobDetailModal' })

const props = defineProps<ScheduledJobDetailModalProps>()
const emit = defineEmits<{ 'update:show': [value: boolean] }>()
const { t } = useLocale()

const displayValue = (value: string | null): string => value || t('job.noValue')
</script>

<template>
  <NModal
    :show="props.show"
    preset="card"
    class="job-detail-modal"
    :title="t('job.detailTitle')"
    @update:show="emit('update:show', $event)"
  >
    <NSpin :show="props.loading">
      <NEmpty v-if="!props.item && !props.loading" :description="t('job.empty')" />
      <NDescriptions
        v-else-if="props.item"
        bordered
        :column="2"
        label-placement="left"
        size="small"
      >
        <NDescriptionsItem :label="t('job.form.name')">
          {{ props.item.job_name }}
        </NDescriptionsItem>
        <NDescriptionsItem :label="t('job.form.key')">
          {{ props.item.job_key }}
        </NDescriptionsItem>
        <NDescriptionsItem :label="t('job.form.taskName')" :span="2">
          {{ props.item.task_name }}
        </NDescriptionsItem>
        <NDescriptionsItem :label="t('job.form.cron')">
          {{ props.item.cron_expression }}
        </NDescriptionsItem>
        <NDescriptionsItem :label="t('job.form.status')">
          <NTag :type="props.item.status === '1' ? 'success' : 'default'" size="small">
            {{ props.item.status === '1' ? t('job.status.enabled') : t('job.status.disabled') }}
          </NTag>
        </NDescriptionsItem>
        <NDescriptionsItem :label="t('job.form.timeout')">
          {{ t('job.seconds').replace('{count}', String(props.item.timeout_seconds)) }}
        </NDescriptionsItem>
        <NDescriptionsItem :label="t('job.form.retries')">
          {{ props.item.max_retries }}
        </NDescriptionsItem>
        <NDescriptionsItem :label="t('job.column.lastStatus')">
          <NTag :type="getJobExecutionStatusTone(props.item.last_status)" size="small">
            {{ getJobExecutionStatusLabel(props.item.last_status, t) }}
          </NTag>
        </NDescriptionsItem>
        <NDescriptionsItem :label="t('job.column.lastRunTime')">
          {{ formatDateTime(props.item.last_run_time, { fallback: t('job.noValue') }) }}
        </NDescriptionsItem>
        <NDescriptionsItem :label="t('job.column.nextRunTime')">
          {{ formatDateTime(props.item.next_run_time, { fallback: t('job.noValue') }) }}
        </NDescriptionsItem>
        <NDescriptionsItem :label="t('job.detail.creator')">
          {{ props.item.create_by ?? t('job.noValue') }}
        </NDescriptionsItem>
        <NDescriptionsItem :label="t('job.detail.createTime')">
          {{ formatDateTime(props.item.create_time, { fallback: t('job.noValue') }) }}
        </NDescriptionsItem>
        <NDescriptionsItem :label="t('job.detail.updateTime')">
          {{ formatDateTime(props.item.update_time, { fallback: t('job.noValue') }) }}
        </NDescriptionsItem>
        <NDescriptionsItem :label="t('job.detail.lastMessage')" :span="2">
          {{ displayValue(props.item.last_message) }}
        </NDescriptionsItem>
        <NDescriptionsItem :label="t('job.form.arguments')" :span="2">
          <pre class="job-json-content">{{ props.item.args_json }}</pre>
        </NDescriptionsItem>
      </NDescriptions>
    </NSpin>
  </NModal>
</template>

<style lang="scss">
.n-card.job-detail-modal {
  width: min(860px, calc(100vw - 32px));
}

.job-json-content {
  max-height: 260px;
  margin: 0;
  overflow: auto;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
  font-size: 12px;
}
</style>
