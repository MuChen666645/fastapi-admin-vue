<script setup lang="ts">
import { computed, h, withDirectives } from 'vue'
import type { VNode } from 'vue'
import { CreateOutline, EyeOutline, ListOutline, TrashOutline } from '@vicons/ionicons5'
import { NButton, NDataTable, NEmpty, NIcon, NTag } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'

import { permissionDirective } from '@/directives'
import { useLocale } from '@/hooks'
import type { DictTypeListItem } from '@/types'
import { formatDateTime } from '@/utils'

defineOptions({ name: 'DictTypeTable' })

interface DictTypeTableProps {
  data: DictTypeListItem[]
  loading: boolean
}

const props = defineProps<DictTypeTableProps>()
const emit = defineEmits<{
  detail: [item: DictTypeListItem]
  viewData: [item: DictTypeListItem]
  edit: [item: DictTypeListItem]
  delete: [item: DictTypeListItem]
}>()

const { t } = useLocale()

const withPermission = (node: VNode, permission: string): VNode =>
  withDirectives(node, [[permissionDirective, permission]])

const columns = computed<DataTableColumns<DictTypeListItem>>(() => [
  {
    title: t('dict.type.column.name'),
    key: 'dict_name',
    minWidth: 180,
    ellipsis: { tooltip: true },
  },
  {
    title: t('dict.type.column.code'),
    key: 'dict_type',
    minWidth: 220,
    ellipsis: { tooltip: true },
  },
  {
    title: t('dict.type.column.status'),
    key: 'status',
    width: 110,
    render: (item) =>
      h(
        NTag,
        { type: item.status === '1' ? 'success' : 'default', size: 'small' },
        {
          default: () =>
            item.status === '1' ? t('dict.status.enabled') : t('dict.status.disabled'),
        },
      ),
  },
  {
    title: t('dict.type.column.remark'),
    key: 'remark',
    minWidth: 220,
    ellipsis: { tooltip: true },
    render: (item) => item.remark ?? t('dict.noValue'),
  },
  {
    title: t('dict.column.updateTime'),
    key: 'update_time',
    width: 180,
    render: (item) => formatDateTime(item.update_time, { fallback: t('dict.noValue') }),
  },
  {
    title: t('dict.column.action'),
    key: 'action',
    width: 210,
    fixed: 'right',
    render: (item) =>
      h('div', { class: 'dict-row-actions' }, [
        withPermission(
          h(
            NButton,
            {
              quaternary: true,
              circle: true,
              'aria-label': t('dict.action.detail'),
              title: t('dict.action.detail'),
              onClick: () => emit('detail', item),
            },
            { icon: () => h(NIcon, null, { default: () => h(EyeOutline) }) },
          ),
          'system:dict:query',
        ),
        withPermission(
          h(
            NButton,
            {
              quaternary: true,
              circle: true,
              'aria-label': t('dict.action.viewData'),
              title: t('dict.action.viewData'),
              onClick: () => emit('viewData', item),
            },
            { icon: () => h(NIcon, null, { default: () => h(ListOutline) }) },
          ),
          'system:dict:list',
        ),
        withPermission(
          h(
            NButton,
            {
              quaternary: true,
              circle: true,
              'aria-label': t('dict.action.edit'),
              title: t('dict.action.edit'),
              onClick: () => emit('edit', item),
            },
            { icon: () => h(NIcon, null, { default: () => h(CreateOutline) }) },
          ),
          'system:dict:edit',
        ),
        withPermission(
          h(
            NButton,
            {
              quaternary: true,
              circle: true,
              type: 'error',
              'aria-label': t('dict.action.delete'),
              title: t('dict.action.delete'),
              onClick: () => emit('delete', item),
            },
            { icon: () => h(NIcon, null, { default: () => h(TrashOutline) }) },
          ),
          'system:dict:remove',
        ),
      ]),
  },
])

const rowKey = (item: DictTypeListItem): number => item.dict_id
</script>

<template>
  <NDataTable
    :columns="columns"
    :data="props.data"
    :loading="props.loading"
    :scroll-x="1100"
    remote
    :row-key="rowKey"
  >
    <template #empty><NEmpty :description="t('dict.type.empty')" /></template>
  </NDataTable>
</template>

<style lang="scss" scoped>
.dict-row-actions {
  display: flex;
  align-items: center;
  gap: 2px;
}
</style>
