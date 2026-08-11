<script setup lang="ts">
import { computed, h, withDirectives } from 'vue'
import type { VNode } from 'vue'
import { CreateOutline, EyeOutline, KeyOutline, TrashOutline } from '@vicons/ionicons5'
import { NButton, NDataTable, NEmpty, NIcon, NTag } from 'naive-ui'
import type { DataTableColumns, DataTableRowKey } from 'naive-ui'

import DictTag from '@/components/DictTag/index.vue'
import { useLocale } from '@/hooks'
import { permissionDirective } from '@/directives'
import type { UserListItem, UserTableProps } from '@/types'
import { formatDateTime, isProtectedAdminUser } from '@/utils'

defineOptions({ name: 'UserTable' })

const props = defineProps<UserTableProps>()

const emit = defineEmits<{
  detail: [item: UserListItem]
  edit: [item: UserListItem]
  'reset-password': [item: UserListItem]
  delete: [item: UserListItem]
  'update:selected-row-keys': [keys: number[]]
}>()

const { t } = useLocale()

const displayValue = (value: string | null): string => value ?? t('user.noValue')

const formatTimestamp = (value: string | null): string =>
  value ? formatDateTime(value, { fallback: t('user.noValue') }) : t('user.noValue')

const withPermission = (node: VNode, permission: string): VNode =>
  withDirectives(node, [[permissionDirective, permission]])

const isProtectedUser = (item: UserListItem): boolean => isProtectedAdminUser(item.username)

const renderActions = (item: UserListItem) =>
  h('div', { class: 'user-row-actions' }, [
    withPermission(
      h(
        NButton,
        {
          quaternary: true,
          circle: true,
          'aria-label': t('user.action.detail'),
          title: t('user.action.detail'),
          onClick: () => emit('detail', item),
        },
        { icon: () => h(NIcon, null, { default: () => h(EyeOutline) }) },
      ),
      'system:user:query',
    ),
    ...(!isProtectedUser(item)
      ? [
          withPermission(
            h(
              NButton,
              {
                quaternary: true,
                circle: true,
                'aria-label': t('user.action.edit'),
                title: t('user.action.edit'),
                onClick: () => emit('edit', item),
              },
              { icon: () => h(NIcon, null, { default: () => h(CreateOutline) }) },
            ),
            'system:user:edit',
          ),
          withPermission(
            h(
              NButton,
              {
                quaternary: true,
                circle: true,
                'aria-label': t('user.action.resetPassword'),
                title: t('user.action.resetPassword'),
                onClick: () => emit('reset-password', item),
              },
              { icon: () => h(NIcon, null, { default: () => h(KeyOutline) }) },
            ),
            'system:user:resetPwd',
          ),
          withPermission(
            h(
              NButton,
              {
                quaternary: true,
                circle: true,
                type: 'error',
                'aria-label': t('user.action.delete'),
                title: t('user.action.delete'),
                onClick: () => emit('delete', item),
              },
              { icon: () => h(NIcon, null, { default: () => h(TrashOutline) }) },
            ),
            'system:user:remove',
          ),
        ]
      : []),
  ])

const columns = computed<DataTableColumns<UserListItem>>(() => {
  const dataColumns: DataTableColumns<UserListItem> = [
    {
      title: t('user.column.username'),
      key: 'username',
      width: 150,
      ellipsis: { tooltip: true },
    },
    {
      title: t('user.column.nickname'),
      key: 'nickname',
      width: 140,
      render: (item) => displayValue(item.nickname),
    },
    {
      title: t('user.column.sex'),
      key: 'sex',
      width: 100,
      render: (item) =>
        item.sex === null
          ? t('user.noValue')
          : h(DictTag, { options: props.sexOptions, value: item.sex }),
    },
    {
      title: t('user.column.phone'),
      key: 'phone',
      width: 150,
      render: (item) => displayValue(item.phone),
    },
    {
      title: t('user.column.email'),
      key: 'email',
      width: 220,
      ellipsis: { tooltip: true },
      render: (item) => displayValue(item.email),
    },
    {
      title: t('user.column.department'),
      key: 'dept_id',
      width: 150,
      render: (item) => props.departmentNames[item.dept_id ?? 0] ?? t('user.noValue'),
    },
    {
      title: t('user.column.status'),
      key: 'status',
      width: 100,
      render: (item) =>
        h(
          NTag,
          { type: item.status === '1' ? 'success' : 'default', size: 'small' },
          {
            default: () =>
              item.status === '1' ? t('user.status.enabled') : t('user.status.disabled'),
          },
        ),
    },
    {
      title: t('user.column.createTime'),
      key: 'create_time',
      width: 180,
      render: (item) => formatTimestamp(item.create_time),
    },
    {
      title: t('user.column.action'),
      key: 'action',
      width: 180,
      fixed: 'right',
      render: renderActions,
    },
  ]

  return [{ type: 'selection' as const, multiple: true, disabled: isProtectedUser }, ...dataColumns]
})

const rowKey = (item: UserListItem): number => item.id

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
    :scroll-x="1420"
    :checked-row-keys="props.selectedRowKeys"
    remote
    :row-key="rowKey"
    @update:checked-row-keys="handleCheckedRowKeys"
  >
    <template #empty><NEmpty :description="t('user.empty')" /></template>
  </NDataTable>
</template>

<style lang="scss" scoped>
.user-row-actions {
  display: flex;
  align-items: center;
  gap: 2px;
}
</style>
