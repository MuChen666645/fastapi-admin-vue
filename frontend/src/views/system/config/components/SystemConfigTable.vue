<script setup lang="ts">
import { computed, h, withDirectives } from 'vue'
import type { VNode } from 'vue'
import { CreateOutline, EyeOutline, TrashOutline } from '@vicons/ionicons5'
import { NButton, NDataTable, NEmpty, NIcon, NTag } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'

import { permissionDirective } from '@/directives'
import { useLocale } from '@/hooks'
import type { SystemConfig, SystemConfigTableProps } from '@/types'
import { formatDateTime } from '@/utils'

defineOptions({ name: 'SystemConfigTable' })

const props = defineProps<SystemConfigTableProps>()
const emit = defineEmits<{
  detail: [item: SystemConfig]
  edit: [item: SystemConfig]
  delete: [item: SystemConfig]
}>()

const { t } = useLocale()

const displayValue = (value: string | null): string => value || t('systemConfig.noValue')
const withPermission = (node: VNode, permission: string): VNode =>
  withDirectives(node, [[permissionDirective, permission]])

const renderActions = (item: SystemConfig): VNode => {
  const actions: VNode[] = []

  if (props.permissions.query) {
    actions.push(
      withPermission(
        h(
          NButton,
          {
            quaternary: true,
            circle: true,
            'aria-label': t('systemConfig.action.detail'),
            title: t('systemConfig.action.detail'),
            onClick: () => emit('detail', item),
          },
          { icon: () => h(NIcon, null, { default: () => h(EyeOutline) }) },
        ),
        'system:config:query',
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
            'aria-label': t('systemConfig.action.edit'),
            title: t('systemConfig.action.edit'),
            onClick: () => emit('edit', item),
          },
          { icon: () => h(NIcon, null, { default: () => h(CreateOutline) }) },
        ),
        'system:config:edit',
      ),
    )
  }

  if (props.permissions.remove && (!item.is_builtin || props.permissions.removeBuiltin)) {
    actions.push(
      withPermission(
        h(
          NButton,
          {
            quaternary: true,
            circle: true,
            type: 'error',
            'aria-label': t('systemConfig.action.delete'),
            title: t('systemConfig.action.delete'),
            onClick: () => emit('delete', item),
          },
          { icon: () => h(NIcon, null, { default: () => h(TrashOutline) }) },
        ),
        'system:config:remove',
      ),
    )
  }

  return h('div', { class: 'system-config-row-actions' }, actions)
}

const columns = computed<DataTableColumns<SystemConfig>>(() => {
  const dataColumns: DataTableColumns<SystemConfig> = [
    {
      title: t('systemConfig.column.name'),
      key: 'config_name',
      width: 180,
      ellipsis: { tooltip: true },
    },
    {
      title: t('systemConfig.column.key'),
      key: 'config_key',
      width: 220,
      ellipsis: { tooltip: true },
    },
    {
      title: t('systemConfig.column.value'),
      key: 'config_value',
      minWidth: 240,
      ellipsis: { tooltip: true },
      render: (item) => displayValue(item.config_value),
    },
    {
      title: t('systemConfig.column.type'),
      key: 'config_type',
      width: 120,
      ellipsis: { tooltip: true },
    },
    {
      title: t('systemConfig.column.builtin'),
      key: 'is_builtin',
      width: 110,
      render: (item) =>
        item.is_builtin
          ? h(
              NTag,
              { size: 'small', type: 'info' },
              { default: () => t('systemConfig.action.builtin') },
            )
          : '-',
    },
    {
      title: t('systemConfig.column.remark'),
      key: 'remark',
      width: 220,
      ellipsis: { tooltip: true },
      render: (item) => displayValue(item.remark),
    },
    {
      title: t('systemConfig.column.updateTime'),
      key: 'update_time',
      width: 180,
      render: (item) => formatDateTime(item.update_time, { fallback: t('systemConfig.noValue') }),
    },
  ]

  if (props.permissions.query || props.permissions.edit || props.permissions.remove) {
    dataColumns.push({
      title: t('systemConfig.column.action'),
      key: 'action',
      width: 150,
      fixed: 'right',
      render: renderActions,
    })
  }

  return dataColumns
})

const rowKey = (item: SystemConfig): number => item.id
</script>

<template>
  <NDataTable
    :columns="columns"
    :data="props.data"
    :loading="props.loading"
    :scroll-x="1380"
    :row-key="rowKey"
    remote
  >
    <template #empty><NEmpty :description="t('systemConfig.empty')" /></template>
  </NDataTable>
</template>

<style lang="scss" scoped>
.system-config-row-actions {
  display: flex;
  align-items: center;
  gap: 2px;
}
</style>
