<script setup lang="ts">
import { computed, h, withDirectives } from 'vue'
import type { VNode } from 'vue'
import { CreateOutline, EyeOutline, TrashOutline } from '@vicons/ionicons5'
import { NButton, NDataTable, NEmpty, NIcon, NTag } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'

import { permissionDirective } from '@/directives'
import { useLocale } from '@/hooks'
import type { PostListItem, PostTableProps } from '@/types'
import { formatDateTime } from '@/utils'

defineOptions({ name: 'PostTable' })

const props = defineProps<PostTableProps>()
const emit = defineEmits<{
  detail: [item: PostListItem]
  edit: [item: PostListItem]
  delete: [item: PostListItem]
}>()

const { t } = useLocale()

const displayValue = (value: string | null): string => value || t('post.noValue')
const withPermission = (node: VNode, permission: string): VNode =>
  withDirectives(node, [[permissionDirective, permission]])

const renderActions = (item: PostListItem): VNode => {
  const actions: VNode[] = []

  if (props.permissions.query) {
    actions.push(
      withPermission(
        h(
          NButton,
          {
            quaternary: true,
            circle: true,
            'aria-label': t('post.action.detail'),
            title: t('post.action.detail'),
            onClick: () => emit('detail', item),
          },
          { icon: () => h(NIcon, null, { default: () => h(EyeOutline) }) },
        ),
        'system:post:query',
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
            'aria-label': t('post.action.edit'),
            title: t('post.action.edit'),
            onClick: () => emit('edit', item),
          },
          { icon: () => h(NIcon, null, { default: () => h(CreateOutline) }) },
        ),
        'system:post:edit',
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
            'aria-label': t('post.action.delete'),
            title: t('post.action.delete'),
            onClick: () => emit('delete', item),
          },
          { icon: () => h(NIcon, null, { default: () => h(TrashOutline) }) },
        ),
        'system:post:remove',
      ),
    )
  }

  return h('div', { class: 'post-row-actions' }, actions)
}

const columns = computed<DataTableColumns<PostListItem>>(() => {
  const dataColumns: DataTableColumns<PostListItem> = [
    {
      title: t('post.column.code'),
      key: 'post_code',
      width: 170,
      ellipsis: { tooltip: true },
    },
    {
      title: t('post.column.name'),
      key: 'post_name',
      width: 170,
      ellipsis: { tooltip: true },
    },
    {
      title: t('post.column.sort'),
      key: 'post_sort',
      width: 90,
    },
    {
      title: t('post.column.status'),
      key: 'status',
      width: 100,
      render: (item) =>
        h(
          NTag,
          { size: 'small', type: item.status === '1' ? 'success' : 'default' },
          {
            default: () =>
              item.status === '1' ? t('post.status.enabled') : t('post.status.disabled'),
          },
        ),
    },
    {
      title: t('post.column.remark'),
      key: 'remark',
      width: 260,
      ellipsis: { tooltip: true },
      render: (item) => displayValue(item.remark),
    },
    {
      title: t('post.column.updateTime'),
      key: 'update_time',
      width: 180,
      render: (item) => formatDateTime(item.update_time, { fallback: t('post.noValue') }),
    },
  ]

  const hasActions = Object.entries(props.permissions).some(
    ([permission, enabled]) => permission !== 'list' && enabled,
  )
  if (hasActions) {
    dataColumns.push({
      title: t('post.column.action'),
      key: 'action',
      width: 140,
      fixed: 'right',
      render: renderActions,
    })
  }

  return dataColumns
})

const rowKey = (item: PostListItem): number => item.post_id
</script>

<template>
  <NDataTable
    :columns="columns"
    :data="props.data"
    :loading="props.loading"
    :scroll-x="1110"
    :row-key="rowKey"
    remote
  >
    <template #empty><NEmpty :description="t('post.empty')" /></template>
  </NDataTable>
</template>

<style lang="scss" scoped>
.post-row-actions {
  display: flex;
  align-items: center;
  gap: 2px;
}
</style>
