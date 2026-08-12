<script setup lang="ts">
import { computed, h } from 'vue'
import { RefreshOutline } from '@vicons/ionicons5'
import { NAlert, NButton, NDataTable, NEmpty, NIcon, NModal, NPagination, NTag } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'

import { useLocale } from '@/hooks'
import type { ScheduledJobLog, ScheduledJobLogModalProps } from '@/types'
import { formatDateTime } from '@/utils'
import { getJobExecutionStatusLabel, getJobExecutionStatusTone } from '../presentation'

defineOptions({ name: 'JobLogModal' })

const props = defineProps<ScheduledJobLogModalProps>()
const emit = defineEmits<{
  'update:show': [value: boolean]
  refresh: []
}>()
const { t } = useLocale()

const displayValue = (value: string | null): string => value || t('job.noValue')
const displayDuration = (value: number | null): string =>
  value === null ? t('job.noValue') : t('job.milliseconds').replace('{count}', String(value))

const columns = computed<DataTableColumns<ScheduledJobLog>>(() => [
  {
    title: t('job.log.column.status'),
    key: 'status',
    width: 110,
    render: (item) =>
      h(
        NTag,
        { size: 'small', type: getJobExecutionStatusTone(item.status) },
        { default: () => getJobExecutionStatusLabel(item.status, t) },
      ),
  },
  {
    title: t('job.log.column.taskName'),
    key: 'task_name',
    width: 220,
    ellipsis: { tooltip: true },
  },
  {
    title: t('job.log.column.message'),
    key: 'message',
    minWidth: 260,
    ellipsis: { tooltip: true },
    render: (item) => displayValue(item.message),
  },
  {
    title: t('job.log.column.startTime'),
    key: 'start_time',
    width: 180,
    render: (item) => formatDateTime(item.start_time, { fallback: t('job.noValue') }),
  },
  {
    title: t('job.log.column.endTime'),
    key: 'end_time',
    width: 180,
    render: (item) => formatDateTime(item.end_time, { fallback: t('job.noValue') }),
  },
  {
    title: t('job.log.column.duration'),
    key: 'duration_ms',
    width: 120,
    render: (item) => displayDuration(item.duration_ms),
  },
])

const rowKey = (item: ScheduledJobLog): number => item.id
</script>

<template>
  <NModal
    :show="props.show"
    preset="card"
    class="job-log-modal"
    :title="t('job.log.title').replace('{name}', props.job?.job_name ?? t('job.noValue'))"
    @update:show="emit('update:show', $event)"
  >
    <div class="job-log-toolbar">
      <span>{{ t('job.log.total').replace('{count}', String(props.pagination.itemCount)) }}</span>
      <NButton
        v-permission="'monitor:job:query'"
        quaternary
        circle
        :loading="props.loading"
        :aria-label="t('job.log.refresh')"
        :title="t('job.log.refresh')"
        @click="emit('refresh')"
      >
        <template #icon
          ><NIcon><RefreshOutline /></NIcon
        ></template>
      </NButton>
    </div>

    <NAlert v-if="props.hasError" type="error" :show-icon="false" class="job-log-error">
      {{ t('job.log.loadFailed') }}
    </NAlert>

    <NDataTable
      :columns="columns"
      :data="props.data"
      :loading="props.loading"
      :scroll-x="1070"
      :row-key="rowKey"
      remote
    >
      <template #empty><NEmpty :description="t('job.log.empty')" /></template>
    </NDataTable>

    <footer class="job-log-footer">
      <NPagination v-bind="props.pagination" />
    </footer>
  </NModal>
</template>

<style lang="scss">
.n-card.job-log-modal {
  width: min(1120px, calc(100vw - 32px));
}

.job-log-toolbar,
.job-log-footer {
  display: flex;
  align-items: center;
}

.job-log-toolbar {
  justify-content: flex-end;
  gap: 8px;
  margin-bottom: 12px;
  color: var(--app-color-text-muted);
  font-size: 13px;
}

.job-log-error {
  margin-bottom: 12px;
}

.job-log-footer {
  justify-content: flex-end;
  min-height: 56px;
  padding-top: 12px;
}
</style>
