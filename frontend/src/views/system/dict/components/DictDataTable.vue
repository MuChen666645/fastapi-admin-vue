<script setup lang="ts">
import { computed, h, withDirectives } from 'vue'
import type { VNode } from 'vue'
import { CreateOutline, EyeOutline, TrashOutline } from '@vicons/ionicons5'
import { NButton, NDataTable, NEmpty, NIcon, NTag } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'

import { permissionDirective } from '@/directives'
import { useLocale } from '@/hooks'
import type { DictDataListItem } from '@/types'
import { formatDateTime } from '@/utils'

defineOptions({ name: 'DictDataTable' })

interface DictDataTableProps {
  data: DictDataListItem[]
  loading: boolean
}

const props = defineProps<DictDataTableProps>()
const emit = defineEmits<{
  detail: [item: DictDataListItem]
  edit: [item: DictDataListItem]
  delete: [item: DictDataListItem]
}>()

const { t } = useLocale()

const withPermission = (node: VNode, permission: string): VNode =>
  withDirectives(node, [[permissionDirective, permission]])

const columns = computed<DataTableColumns<DictDataListItem>>(() => [
  {
    title: t('dict.data.column.sort'),
    key: 'dict_sort',
    width: 90,
  },
  {
    title: t('dict.data.column.label'),
    key: 'dict_label',
    minWidth: 180,
    ellipsis: { tooltip: true },
  },
  {
    title: t('dict.data.column.value'),
    key: 'dict_value',
    minWidth: 180,
    ellipsis: { tooltip: true },
  },
  {
    title: t('dict.data.column.type'),
    key: 'dict_type',
    minWidth: 180,
    ellipsis: { tooltip: true },
  },
  {
    title: t('dict.data.column.status'),
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
    title: t('dict.column.updateTime'),
    key: 'update_time',
    width: 180,
    render: (item) => formatDateTime(item.update_time, { fallback: t('dict.noValue') }),
  },
  {
    title: t('dict.column.action'),
    key: 'action',
    width: 170,
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

const rowKey = (item: DictDataListItem): number => item.dict_code
</script>

<template>
  <NDataTable
    :columns="columns"
    :data="props.data"
    :loading="props.loading"
    :scroll-x="1150"
    remote
    :row-key="rowKey"
  >
    <template #empty><NEmpty :description="t('dict.data.empty')" /></template>
  </NDataTable>
</template>

<style lang="scss" scoped>
.dict-row-actions {
  display: flex;
  align-items: center;
  gap: 2px;
}
</style>
