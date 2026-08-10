<script setup lang="ts">
import { computed, h, withDirectives } from 'vue'
import type { VNode } from 'vue'
import { AddOutline, CreateOutline, EyeOutline, TrashOutline } from '@vicons/ionicons5'
import { NButton, NDataTable, NEmpty, NIcon, NTag } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'

import { permissionDirective } from '@/directives'
import { useLocale } from '@/hooks'
import type { MenuItem, MenuType } from '@/types'
import { formatDateTime } from '@/utils'

defineOptions({ name: 'MenuTable' })

interface MenuTableProps {
  data: MenuItem[]
  loading: boolean
}

const props = defineProps<MenuTableProps>()
const emit = defineEmits<{
  detail: [item: MenuItem]
  createChild: [item: MenuItem]
  edit: [item: MenuItem]
  delete: [item: MenuItem]
}>()

const { t } = useLocale()

const menuTypeLabel = (value: MenuType): string => {
  switch (value) {
    case 'C':
      return t('menuManagement.type.router')
    case 'F':
      return t('menuManagement.type.button')
    case 'L':
      return t('menuManagement.type.link')
    case 'I':
      return t('menuManagement.type.iframe')
  }
}

const displayValue = (value: string | number | null): string =>
  value === null || value === '' ? t('menuManagement.noValue') : String(value)

const withPermission = (node: VNode, permission: string): VNode =>
  withDirectives(node, [[permissionDirective, permission]])

const renderActions = (item: MenuItem): VNode =>
  h('div', { class: 'menu-row-actions' }, [
    withPermission(
      h(
        NButton,
        {
          quaternary: true,
          circle: true,
          'aria-label': t('menuManagement.action.detail'),
          title: t('menuManagement.action.detail'),
          onClick: () => emit('detail', item),
        },
        { icon: () => h(NIcon, null, { default: () => h(EyeOutline) }) },
      ),
      'system:menu:query',
    ),
    ...(item.menu_type !== 'F'
      ? [
          withPermission(
            h(
              NButton,
              {
                quaternary: true,
                circle: true,
                'aria-label': t('menuManagement.action.createChild'),
                title: t('menuManagement.action.createChild'),
                onClick: () => emit('createChild', item),
              },
              { icon: () => h(NIcon, null, { default: () => h(AddOutline) }) },
            ),
            'system:menu:add',
          ),
        ]
      : []),
    withPermission(
      h(
        NButton,
        {
          quaternary: true,
          circle: true,
          'aria-label': t('menuManagement.action.edit'),
          title: t('menuManagement.action.edit'),
          onClick: () => emit('edit', item),
        },
        { icon: () => h(NIcon, null, { default: () => h(CreateOutline) }) },
      ),
      'system:menu:edit',
    ),
    withPermission(
      h(
        NButton,
        {
          quaternary: true,
          circle: true,
          type: 'error',
          'aria-label': t('menuManagement.action.delete'),
          title: t('menuManagement.action.delete'),
          onClick: () => emit('delete', item),
        },
        { icon: () => h(NIcon, null, { default: () => h(TrashOutline) }) },
      ),
      'system:menu:remove',
    ),
  ])

const columns = computed<DataTableColumns<MenuItem>>(() => [
  {
    title: t('menuManagement.column.name'),
    key: 'menu_name',
    width: 210,
    tree: true,
    ellipsis: { tooltip: true },
  },
  {
    title: t('menuManagement.column.type'),
    key: 'menu_type',
    width: 110,
    render: (item) =>
      h(
        NTag,
        { size: 'small', type: item.menu_type === 'F' ? 'warning' : 'info' },
        { default: () => menuTypeLabel(item.menu_type) },
      ),
  },
  {
    title: t('menuManagement.column.path'),
    key: 'menu_path',
    width: 220,
    ellipsis: { tooltip: true },
    render: (item) => displayValue(item.menu_path),
  },
  {
    title: t('menuManagement.column.component'),
    key: 'component',
    width: 180,
    ellipsis: { tooltip: true },
    render: (item) => displayValue(item.component),
  },
  {
    title: t('menuManagement.column.permission'),
    key: 'perms',
    width: 190,
    ellipsis: { tooltip: true },
    render: (item) => displayValue(item.perms),
  },
  {
    title: t('menuManagement.column.status'),
    key: 'status',
    width: 100,
    render: (item) =>
      h(
        NTag,
        { size: 'small', type: item.status === '1' ? 'success' : 'default' },
        {
          default: () =>
            item.status === '1'
              ? t('menuManagement.status.enabled')
              : t('menuManagement.status.disabled'),
        },
      ),
  },
  {
    title: t('menuManagement.column.sort'),
    key: 'sort',
    width: 80,
    render: (item) => displayValue(item.sort),
  },
  {
    title: t('menuManagement.column.updateTime'),
    key: 'update_time',
    width: 180,
    render: (item) => formatDateTime(item.update_time, { fallback: t('menuManagement.noValue') }),
  },
  {
    title: t('menuManagement.column.action'),
    key: 'action',
    width: 170,
    fixed: 'right',
    render: renderActions,
  },
])

const rowKey = (item: MenuItem): number => item.menu_id
</script>

<template>
  <NDataTable
    :columns="columns"
    :data="props.data"
    :loading="props.loading"
    :scroll-x="1450"
    :row-key="rowKey"
    children-key="children"
  >
    <template #empty><NEmpty :description="t('menuManagement.empty')" /></template>
  </NDataTable>
</template>

<style lang="scss" scoped>
.menu-row-actions {
  display: flex;
  align-items: center;
  gap: 2px;
}
</style>
