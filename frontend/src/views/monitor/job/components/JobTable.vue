<script setup lang="ts">
import { computed, h, withDirectives } from 'vue'
import type { VNode } from 'vue'
import {
  CreateOutline,
  EyeOutline,
  ListOutline,
  PlayOutline,
  TrashOutline,
} from '@vicons/ionicons5'
import { NButton, NDataTable, NEmpty, NIcon, NTag } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'

import { permissionDirective } from '@/directives'
import { useLocale } from '@/hooks'
import type { ScheduledJob, ScheduledJobTableProps } from '@/types'
import { formatDateTime } from '@/utils'
import { getJobExecutionStatusLabel, getJobExecutionStatusTone } from '../presentation'

defineOptions({ name: 'JobTable' })

const props = defineProps<ScheduledJobTableProps>()
const emit = defineEmits<{
  detail: [item: ScheduledJob]
  edit: [item: ScheduledJob]
  run: [item: ScheduledJob]
  logs: [item: ScheduledJob]
  delete: [item: ScheduledJob]
}>()
const { t } = useLocale()

const withPermission = (node: VNode, permission: string): VNode =>
  withDirectives(node, [[permissionDirective, permission]])

const emitAction = (
  event: 'detail' | 'edit' | 'run' | 'logs' | 'delete',
  item: ScheduledJob,
): void => {
  switch (event) {
    case 'detail':
      emit('detail', item)
      break
    case 'edit':
      emit('edit', item)
      break
    case 'run':
      emit('run', item)
      break
    case 'logs':
      emit('logs', item)
      break
    case 'delete':
      emit('delete', item)
  }
}

const renderIconAction = (
  item: ScheduledJob,
  label: string,
  icon: VNode,
  event: 'detail' | 'edit' | 'run' | 'logs' | 'delete',
  permission: string,
  options: { disabled?: boolean; loading?: boolean; type?: 'error' | 'primary' } = {},
): VNode =>
  withPermission(
    h(
      NButton,
      {
        quaternary: true,
        circle: true,
        type: options.type,
        disabled: options.disabled,
        loading: options.loading,
        'aria-label': label,
        title: label,
        onClick: () => emitAction(event, item),
      },
      { icon: () => h(NIcon, null, { default: () => icon }) },
    ),
    permission,
  )

const renderActions = (item: ScheduledJob): VNode => {
  const actions: VNode[] = []
  const busy = props.processingAction !== null

  if (props.permissions.query) {
    actions.push(
      renderIconAction(item, t('job.action.detail'), h(EyeOutline), 'detail', 'monitor:job:query', {
        disabled: busy,
      }),
      renderIconAction(item, t('job.action.logs'), h(ListOutline), 'logs', 'monitor:job:query', {
        disabled: busy,
      }),
    )
  }

  if (props.permissions.edit) {
    actions.push(
      renderIconAction(item, t('job.action.edit'), h(CreateOutline), 'edit', 'monitor:job:edit', {
        disabled: busy,
      }),
    )
  }

  if (props.permissions.run) {
    actions.push(
      renderIconAction(item, t('job.action.run'), h(PlayOutline), 'run', 'monitor:job:run', {
        disabled: busy || item.status !== '1',
        loading: props.processingAction === `run:${item.id}`,
        type: 'primary',
      }),
    )
  }

  if (props.permissions.remove) {
    actions.push(
      renderIconAction(
        item,
        t('job.action.delete'),
        h(TrashOutline),
        'delete',
        'monitor:job:remove',
        {
          disabled: busy,
          loading: props.processingAction === `delete:${item.id}`,
          type: 'error',
        },
      ),
    )
  }

  return h('div', { class: 'job-row-actions' }, actions)
}

const columns = computed<DataTableColumns<ScheduledJob>>(() => {
  const dataColumns: DataTableColumns<ScheduledJob> = [
    {
      title: t('job.column.name'),
      key: 'job_name',
      width: 170,
      ellipsis: { tooltip: true },
    },
    {
      title: t('job.column.key'),
      key: 'job_key',
      width: 190,
      ellipsis: { tooltip: true },
    },
    {
      title: t('job.column.taskName'),
      key: 'task_name',
      width: 220,
      ellipsis: { tooltip: true },
    },
    {
      title: t('job.column.cron'),
      key: 'cron_expression',
      width: 150,
      ellipsis: { tooltip: true },
    },
    {
      title: t('job.column.status'),
      key: 'status',
      width: 90,
      render: (item) =>
        h(
          NTag,
          { size: 'small', type: item.status === '1' ? 'success' : 'default' },
          {
            default: () =>
              item.status === '1' ? t('job.status.enabled') : t('job.status.disabled'),
          },
        ),
    },
    {
      title: t('job.column.lastStatus'),
      key: 'last_status',
      width: 110,
      render: (item) =>
        h(
          NTag,
          { size: 'small', type: getJobExecutionStatusTone(item.last_status) },
          { default: () => getJobExecutionStatusLabel(item.last_status, t) },
        ),
    },
    {
      title: t('job.column.nextRunTime'),
      key: 'next_run_time',
      width: 180,
      render: (item) => formatDateTime(item.next_run_time, { fallback: t('job.noValue') }),
    },
  ]

  const hasActions = Object.entries(props.permissions).some(
    ([permission, enabled]) => permission !== 'list' && enabled,
  )
  if (hasActions) {
    dataColumns.push({
      title: t('job.column.action'),
      key: 'action',
      width: 200,
      fixed: 'right',
      render: renderActions,
    })
  }

  return dataColumns
})

const rowKey = (item: ScheduledJob): number => item.id
</script>

<template>
  <NDataTable
    :columns="columns"
    :data="props.data"
    :loading="props.loading"
    :scroll-x="1310"
    :row-key="rowKey"
    remote
  >
    <template #empty><NEmpty :description="t('job.empty')" /></template>
  </NDataTable>
</template>

<style lang="scss" scoped>
.job-row-actions {
  display: flex;
  align-items: center;
  gap: 2px;
}
</style>
