<script setup lang="ts">
import { computed, h, withDirectives } from 'vue'
import type { VNode } from 'vue'
import { CreateOutline, EyeOutline, TrashOutline } from '@vicons/ionicons5'
import { NButton, NDataTable, NEmpty, NIcon, NTag } from 'naive-ui'
import type { DataTableColumns, DataTableRowKey } from 'naive-ui'

import { permissionDirective } from '@/directives'
import { useLocale } from '@/hooks'
import type { RoleDataScope, RoleListItem } from '@/types'
import { formatDateTime, isProtectedAdminRole } from '@/utils'

defineOptions({ name: 'RoleTable' })

interface RoleTableProps {
  data: RoleListItem[]
  loading: boolean
  selectedRowKeys: number[]
}

const props = defineProps<RoleTableProps>()
const emit = defineEmits<{
  detail: [item: RoleListItem]
  edit: [item: RoleListItem]
  delete: [item: RoleListItem]
  'update:selected-row-keys': [keys: number[]]
}>()

const { t } = useLocale()

const displayValue = (value: string | null): string => value ?? t('role.noValue')

const formatTimestamp = (value: string): string =>
  formatDateTime(value, { fallback: t('role.noValue') })

const dataScopeLabel = (value: RoleDataScope): string => {
  switch (value) {
    case '1':
      return t('role.dataScope.all')
    case '2':
      return t('role.dataScope.custom')
    case '3':
      return t('role.dataScope.current')
    case '4':
      return t('role.dataScope.currentAndBelow')
    default:
      return t('role.dataScope.self')
  }
}

const withPermission = (node: VNode, permission: string): VNode =>
  withDirectives(node, [[permissionDirective, permission]])

const renderActions = (item: RoleListItem): VNode =>
  h('div', { class: 'role-row-actions' }, [
    withPermission(
      h(
        NButton,
        {
          quaternary: true,
          circle: true,
          'aria-label': t('role.action.detail'),
          title: t('role.action.detail'),
          onClick: () => emit('detail', item),
        },
        { icon: () => h(NIcon, null, { default: () => h(EyeOutline) }) },
      ),
      'system:role:query',
    ),
    ...(!isProtectedAdminRole(item.code)
      ? [
          withPermission(
            h(
              NButton,
              {
                quaternary: true,
                circle: true,
                'aria-label': t('role.action.edit'),
                title: t('role.action.edit'),
                onClick: () => emit('edit', item),
              },
              { icon: () => h(NIcon, null, { default: () => h(CreateOutline) }) },
            ),
            'system:role:edit',
          ),
          withPermission(
            h(
              NButton,
              {
                quaternary: true,
                circle: true,
                type: 'error',
                'aria-label': t('role.action.delete'),
                title: t('role.action.delete'),
                onClick: () => emit('delete', item),
              },
              { icon: () => h(NIcon, null, { default: () => h(TrashOutline) }) },
            ),
            'system:role:remove',
          ),
        ]
      : []),
  ])

const columns = computed<DataTableColumns<RoleListItem>>(() => [
  {
    type: 'selection',
    multiple: true,
    disabled: (item) => isProtectedAdminRole(item.code),
  },
  {
    title: t('role.column.name'),
    key: 'name',
    width: 150,
    ellipsis: { tooltip: true },
  },
  {
    title: t('role.column.code'),
    key: 'code',
    width: 150,
    ellipsis: { tooltip: true },
  },
  {
    title: t('role.column.description'),
    key: 'description',
    width: 240,
    ellipsis: { tooltip: true },
    render: (item) => displayValue(item.description),
  },
  {
    title: t('role.column.dataScope'),
    key: 'data_scope',
    width: 170,
    render: (item) => dataScopeLabel(item.data_scope),
  },
  {
    title: t('role.column.status'),
    key: 'status',
    width: 100,
    render: (item) =>
      h(
        NTag,
        { type: item.status === '1' ? 'success' : 'default', size: 'small' },
        {
          default: () =>
            item.status === '1' ? t('role.status.enabled') : t('role.status.disabled'),
        },
      ),
  },
  {
    title: t('role.column.updateTime'),
    key: 'update_time',
    width: 180,
    render: (item) => formatTimestamp(item.update_time),
  },
  {
    title: t('role.column.action'),
    key: 'action',
    width: 140,
    fixed: 'right',
    render: renderActions,
  },
])

const rowKey = (item: RoleListItem): number => item.id

const handleCheckedRowKeys = (keys: DataTableRowKey[]): void => {
  emit(
    'update:selected-row-keys',
    keys.filter((key): key is number => typeof key === 'number'),
  )
}
</script>

<template>
  <NDataTable
    :columns="columns"
    :data="props.data"
    :loading="props.loading"
    :scroll-x="1300"
    :checked-row-keys="props.selectedRowKeys"
    remote
    :row-key="rowKey"
    @update:checked-row-keys="handleCheckedRowKeys"
  >
    <template #empty><NEmpty :description="t('role.empty')" /></template>
  </NDataTable>
</template>

<style lang="scss" scoped>
.role-row-actions {
  display: flex;
  align-items: center;
  gap: 2px;
}
</style>
