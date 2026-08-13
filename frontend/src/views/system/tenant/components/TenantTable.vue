<script setup lang="ts">
import { computed, h, withDirectives } from 'vue'
import type { VNode } from 'vue'
import { CreateOutline, EyeOutline, PeopleOutline, TrashOutline } from '@vicons/ionicons5'
import { NButton, NDataTable, NEmpty, NIcon, NTag } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'

import { permissionDirective } from '@/directives'
import { useLocale } from '@/hooks'
import type { Tenant, TenantTableProps } from '@/types'
import { formatDateTime } from '@/utils'
import { DEFAULT_TENANT_ID } from '../constants'

defineOptions({ name: 'TenantTable' })

const props = defineProps<TenantTableProps>()
const emit = defineEmits<{
  detail: [item: Tenant]
  members: [item: Tenant]
  edit: [item: Tenant]
  delete: [item: Tenant]
}>()
const { t } = useLocale()

const displayValue = (value: string | null): string => value || t('tenant.noValue')
const withPermission = (node: VNode, permission: string): VNode =>
  withDirectives(node, [[permissionDirective, permission]])

const renderActions = (item: Tenant): VNode => {
  const actions: VNode[] = [
    withPermission(
      h(
        NButton,
        {
          quaternary: true,
          circle: true,
          'aria-label': t('tenant.action.detail'),
          title: t('tenant.action.detail'),
          onClick: () => emit('detail', item),
        },
        { icon: () => h(NIcon, null, { default: () => h(EyeOutline) }) },
      ),
      'system:tenant:list',
    ),
  ]

  if (props.permissions.memberList && item.status === '1') {
    actions.push(
      withPermission(
        h(
          NButton,
          {
            quaternary: true,
            circle: true,
            'aria-label': t('tenant.action.members'),
            title: t('tenant.action.members'),
            onClick: () => emit('members', item),
          },
          { icon: () => h(NIcon, null, { default: () => h(PeopleOutline) }) },
        ),
        'system:tenant:member:list',
      ),
    )
  }

  if (props.permissions.edit && item.id !== DEFAULT_TENANT_ID) {
    actions.push(
      withPermission(
        h(
          NButton,
          {
            quaternary: true,
            circle: true,
            'aria-label': t('tenant.action.edit'),
            title: t('tenant.action.edit'),
            onClick: () => emit('edit', item),
          },
          { icon: () => h(NIcon, null, { default: () => h(CreateOutline) }) },
        ),
        'system:tenant:edit',
      ),
    )
  }

  if (props.permissions.remove && item.id !== DEFAULT_TENANT_ID) {
    actions.push(
      withPermission(
        h(
          NButton,
          {
            quaternary: true,
            circle: true,
            type: 'error',
            'aria-label': t('tenant.action.delete'),
            title: t('tenant.action.delete'),
            onClick: () => emit('delete', item),
          },
          { icon: () => h(NIcon, null, { default: () => h(TrashOutline) }) },
        ),
        'system:tenant:remove',
      ),
    )
  }

  return h('div', { class: 'tenant-row-actions' }, actions)
}

const columns = computed<DataTableColumns<Tenant>>(() => {
  const dataColumns: DataTableColumns<Tenant> = [
    {
      title: t('tenant.column.code'),
      key: 'code',
      width: 180,
      ellipsis: { tooltip: true },
    },
    {
      title: t('tenant.column.name'),
      key: 'name',
      width: 180,
      ellipsis: { tooltip: true },
    },
    {
      title: t('tenant.column.description'),
      key: 'description',
      minWidth: 260,
      ellipsis: { tooltip: true },
      render: (item) => displayValue(item.description),
    },
    {
      title: t('tenant.column.status'),
      key: 'status',
      width: 100,
      render: (item) =>
        h(
          NTag,
          { size: 'small', type: item.status === '1' ? 'success' : 'default' },
          {
            default: () =>
              item.status === '1' ? t('tenant.status.enabled') : t('tenant.status.disabled'),
          },
        ),
    },
    {
      title: t('tenant.column.version'),
      key: 'version',
      width: 90,
    },
    {
      title: t('tenant.column.updateTime'),
      key: 'update_time',
      width: 180,
      render: (item) => formatDateTime(item.update_time, { fallback: t('tenant.noValue') }),
    },
  ]

  dataColumns.push({
    title: t('tenant.column.action'),
    key: 'action',
    width: 190,
    fixed: 'right',
    render: renderActions,
  })

  return dataColumns
})

const rowKey = (item: Tenant): number => item.id
</script>

<template>
  <NDataTable
    :columns="columns"
    :data="props.data"
    :loading="props.loading"
    :scroll-x="1160"
    :row-key="rowKey"
    remote
  >
    <template #empty><NEmpty :description="t('tenant.empty')" /></template>
  </NDataTable>
</template>

<style lang="scss" scoped>
.tenant-row-actions {
  display: flex;
  align-items: center;
  gap: 2px;
}
</style>
