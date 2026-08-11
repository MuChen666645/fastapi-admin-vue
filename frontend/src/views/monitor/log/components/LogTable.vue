<script setup lang="ts">
import { computed, h, withDirectives } from 'vue'
import type { VNode } from 'vue'
import { EyeOutline } from '@vicons/ionicons5'
import { NButton, NDataTable, NEmpty, NIcon, NTag } from 'naive-ui'
import type { DataTableColumns, DataTableRowKey } from 'naive-ui'

import { permissionDirective } from '@/directives'
import { useLocale } from '@/hooks'
import type {
  ExceptionLogItem,
  LoginLogItem,
  LogListItem,
  LogTableProps,
  OperationLogItem,
} from '@/types'
import { formatDateTime } from '@/utils'

defineOptions({ name: 'LogTable' })

const props = defineProps<LogTableProps>()
const emit = defineEmits<{
  detail: [item: LogListItem]
  'update:selected-row-keys': [keys: number[]]
}>()

const { t } = useLocale()

const loginData = computed<LoginLogItem[]>(() =>
  props.data.filter((item): item is LoginLogItem => 'login_time' in item),
)
const operationData = computed<OperationLogItem[]>(() =>
  props.data.filter((item): item is OperationLogItem => 'operation_time' in item),
)
const exceptionData = computed<ExceptionLogItem[]>(() =>
  props.data.filter((item): item is ExceptionLogItem => 'exception_time' in item),
)

const displayValue = (value: string | null): string => value || t('log.noValue')
const withPermission = (node: VNode, permission: string): VNode =>
  withDirectives(node, [[permissionDirective, permission]])

const renderDetailAction = (item: LogListItem, permission: string): VNode =>
  h('div', { class: 'log-row-actions' }, [
    withPermission(
      h(
        NButton,
        {
          quaternary: true,
          circle: true,
          'aria-label': t('log.action.detail'),
          title: t('log.action.detail'),
          onClick: () => emit('detail', item),
        },
        { icon: () => h(NIcon, null, { default: () => h(EyeOutline) }) },
      ),
      permission,
    ),
  ])

const loginColumns = computed<DataTableColumns<LoginLogItem>>(() => [
  { type: 'selection', multiple: true },
  {
    title: t('log.column.username'),
    key: 'username',
    width: 160,
    ellipsis: { tooltip: true },
  },
  {
    title: t('log.column.ipAddress'),
    key: 'ip_address',
    width: 150,
    render: (item) => displayValue(item.ip_address),
  },
  {
    title: t('log.column.userAgent'),
    key: 'user_agent',
    width: 600,
    ellipsis: { tooltip: true },
  },
  {
    title: t('log.column.status'),
    key: 'status',
    width: 100,
    render: (item) =>
      h(
        NTag,
        { size: 'small', type: item.status === '1' ? 'success' : 'error' },
        { default: () => (item.status === '1' ? t('log.status.success') : t('log.status.failed')) },
      ),
  },
  {
    title: t('log.column.message'),
    key: 'message',
    minWidth: 240,
    ellipsis: { tooltip: true },
    render: (item) => displayValue(item.message),
  },
  {
    title: t('log.column.time'),
    key: 'login_time',
    width: 180,
    render: (item) => formatDateTime(item.login_time, { fallback: t('log.noValue') }),
  },
  {
    title: t('log.column.action'),
    key: 'action',
    width: 90,
    fixed: 'right',
    render: (item) => renderDetailAction(item, 'monitor:login:list'),
  },
])

const operationColumns = computed<DataTableColumns<OperationLogItem>>(() => [
  { type: 'selection', multiple: true },
  {
    title: t('log.column.username'),
    key: 'username',
    width: 150,
    render: (item) => displayValue(item.username),
  },
  {
    title: t('log.column.method'),
    key: 'method',
    width: 100,
    render: (item) => h(NTag, { size: 'small' }, { default: () => item.method }),
  },
  {
    title: t('log.column.path'),
    key: 'path',
    minWidth: 240,
    ellipsis: { tooltip: true },
  },
  {
    title: t('log.column.ipAddress'),
    key: 'ip_address',
    width: 150,
    render: (item) => displayValue(item.ip_address),
  },
  {
    title: t('log.column.statusCode'),
    key: 'status_code',
    width: 110,
    render: (item) =>
      h(
        NTag,
        {
          size: 'small',
          type: item.status_code >= 500 ? 'error' : item.status_code >= 400 ? 'warning' : 'success',
        },
        { default: () => String(item.status_code) },
      ),
  },
  {
    title: t('log.column.duration'),
    key: 'duration_ms',
    width: 120,
    render: (item) => t('log.duration').replace('{value}', String(item.duration_ms)),
  },
  {
    title: t('log.column.time'),
    key: 'operation_time',
    width: 180,
    render: (item) => formatDateTime(item.operation_time, { fallback: t('log.noValue') }),
  },
  {
    title: t('log.column.action'),
    key: 'action',
    width: 90,
    fixed: 'right',
    render: (item) => renderDetailAction(item, 'monitor:operation:list'),
  },
])

const exceptionColumns = computed<DataTableColumns<ExceptionLogItem>>(() => [
  { type: 'selection', multiple: true },
  {
    title: t('log.column.username'),
    key: 'username',
    width: 150,
    render: (item) => displayValue(item.username),
  },
  {
    title: t('log.column.method'),
    key: 'method',
    width: 100,
    render: (item) => h(NTag, { size: 'small', type: 'error' }, { default: () => item.method }),
  },
  {
    title: t('log.column.path'),
    key: 'path',
    minWidth: 220,
    ellipsis: { tooltip: true },
  },
  {
    title: t('log.column.ipAddress'),
    key: 'ip_address',
    width: 150,
    render: (item) => displayValue(item.ip_address),
  },
  {
    title: t('log.column.exceptionType'),
    key: 'exception_type',
    width: 180,
    ellipsis: { tooltip: true },
  },
  {
    title: t('log.column.message'),
    key: 'exception_message',
    minWidth: 260,
    ellipsis: { tooltip: true },
  },
  {
    title: t('log.column.time'),
    key: 'exception_time',
    width: 180,
    render: (item) => formatDateTime(item.exception_time, { fallback: t('log.noValue') }),
  },
  {
    title: t('log.column.action'),
    key: 'action',
    width: 90,
    fixed: 'right',
    render: (item) => renderDetailAction(item, 'monitor:exception:list'),
  },
])

const rowKey = (item: LogListItem): number => item.id
const handleCheckedRowKeys = (keys: DataTableRowKey[]): void => {
  emit(
    'update:selected-row-keys',
    keys.filter((key): key is number => typeof key === 'number'),
  )
}
</script>

<template>
  <NDataTable
    v-if="props.kind === 'login'"
    :columns="loginColumns"
    :data="loginData"
    :loading="props.loading"
    :checked-row-keys="props.selectedRowKeys"
    :scroll-x="1110"
    remote
    :row-key="rowKey"
    @update:checked-row-keys="handleCheckedRowKeys"
  >
    <template #empty><NEmpty :description="t('log.empty')" /></template>
  </NDataTable>

  <NDataTable
    v-else-if="props.kind === 'operation'"
    :columns="operationColumns"
    :data="operationData"
    :loading="props.loading"
    :checked-row-keys="props.selectedRowKeys"
    :scroll-x="1400"
    remote
    :row-key="rowKey"
    @update:checked-row-keys="handleCheckedRowKeys"
  >
    <template #empty><NEmpty :description="t('log.empty')" /></template>
  </NDataTable>

  <NDataTable
    v-else
    :columns="exceptionColumns"
    :data="exceptionData"
    :loading="props.loading"
    :checked-row-keys="props.selectedRowKeys"
    :scroll-x="1420"
    remote
    :row-key="rowKey"
    @update:checked-row-keys="handleCheckedRowKeys"
  >
    <template #empty><NEmpty :description="t('log.empty')" /></template>
  </NDataTable>
</template>

<style lang="scss" scoped>
.log-row-actions {
  display: flex;
  align-items: center;
  gap: 2px;
}
</style>
