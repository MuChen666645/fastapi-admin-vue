<script setup lang="ts">
import { computed, h, withDirectives } from 'vue'
import type { VNode } from 'vue'
import { AddOutline, CreateOutline, EyeOutline, TrashOutline } from '@vicons/ionicons5'
import { NButton, NDataTable, NEmpty, NIcon, NTag } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'

import { permissionDirective } from '@/directives'
import { useLocale } from '@/hooks'
import type { DepartmentListItem, DepartmentTableProps } from '@/types'
import { formatDateTime } from '@/utils'

defineOptions({ name: 'DepartmentTable' })

const props = defineProps<DepartmentTableProps>()
const emit = defineEmits<{
  detail: [item: DepartmentListItem]
  createChild: [item: DepartmentListItem]
  edit: [item: DepartmentListItem]
  delete: [item: DepartmentListItem]
}>()

const { t } = useLocale()

const displayValue = (value: string | null): string => value || t('department.noValue')
const withPermission = (node: VNode, permission: string): VNode =>
  withDirectives(node, [[permissionDirective, permission]])

const renderActions = (item: DepartmentListItem): VNode => {
  const actions: VNode[] = []

  if (props.permissions.query) {
    actions.push(
      withPermission(
        h(
          NButton,
          {
            quaternary: true,
            circle: true,
            'aria-label': t('department.action.detail'),
            title: t('department.action.detail'),
            onClick: () => emit('detail', item),
          },
          { icon: () => h(NIcon, null, { default: () => h(EyeOutline) }) },
        ),
        'system:dept:query',
      ),
    )
  }

  if (props.permissions.create) {
    actions.push(
      withPermission(
        h(
          NButton,
          {
            quaternary: true,
            circle: true,
            'aria-label': t('department.action.createChild'),
            title: t('department.action.createChild'),
            onClick: () => emit('createChild', item),
          },
          { icon: () => h(NIcon, null, { default: () => h(AddOutline) }) },
        ),
        'system:dept:add',
      ),
    )
  }

  if (props.permissions.edit) {
    actions.push(
      withPermission(
        h(
          NButton,
          {
            quaternary: true,
            circle: true,
            'aria-label': t('department.action.edit'),
            title: t('department.action.edit'),
            onClick: () => emit('edit', item),
          },
          { icon: () => h(NIcon, null, { default: () => h(CreateOutline) }) },
        ),
        'system:dept:edit',
      ),
    )
  }

  if (props.permissions.remove) {
    actions.push(
      withPermission(
        h(
          NButton,
          {
            quaternary: true,
            circle: true,
            type: 'error',
            'aria-label': t('department.action.delete'),
            title: t('department.action.delete'),
            onClick: () => emit('delete', item),
          },
          { icon: () => h(NIcon, null, { default: () => h(TrashOutline) }) },
        ),
        'system:dept:remove',
      ),
    )
  }

  return h('div', { class: 'department-row-actions' }, actions)
}

const columns = computed<DataTableColumns<DepartmentListItem>>(() => {
  const dataColumns: DataTableColumns<DepartmentListItem> = [
    {
      title: t('department.column.name'),
      key: 'dept_name',
      width: 220,
      tree: true,
      ellipsis: { tooltip: true },
    },
    {
      title: t('department.column.leader'),
      key: 'leader',
      width: 130,
      ellipsis: { tooltip: true },
      render: (item) => displayValue(item.leader),
    },
    {
      title: t('department.column.phone'),
      key: 'phone',
      width: 150,
      render: (item) => displayValue(item.phone),
    },
    {
      title: t('department.column.email'),
      key: 'email',
      width: 220,
      ellipsis: { tooltip: true },
      render: (item) => displayValue(item.email),
    },
    {
      title: t('department.column.status'),
      key: 'status',
      width: 100,
      render: (item) =>
        h(
          NTag,
          { size: 'small', type: item.status === '1' ? 'success' : 'default' },
          {
            default: () =>
              item.status === '1'
                ? t('department.status.enabled')
                : t('department.status.disabled'),
          },
        ),
    },
    {
      title: t('department.column.sort'),
      key: 'order_num',
      width: 90,
    },
    {
      title: t('department.column.updateTime'),
      key: 'update_time',
      width: 180,
      render: (item) => formatDateTime(item.update_time, { fallback: t('department.noValue') }),
    },
  ]

  const hasActions = Object.entries(props.permissions).some(
    ([permission, enabled]) => permission !== 'list' && enabled,
  )
  if (hasActions) {
    dataColumns.push({
      title: t('department.column.action'),
      key: 'action',
      width: 180,
      fixed: 'right',
      render: renderActions,
    })
  }

  return dataColumns
})

const rowKey = (item: DepartmentListItem): number => item.dept_id
</script>

<template>
  <NDataTable
    :columns="columns"
    :data="props.data"
    :loading="props.loading"
    :scroll-x="1270"
    :row-key="rowKey"
    children-key="children"
    default-expand-all
  >
    <template #empty><NEmpty :description="t('department.empty')" /></template>
  </NDataTable>
</template>

<style lang="scss" scoped>
.department-row-actions {
  display: flex;
  align-items: center;
  gap: 2px;
}
</style>
