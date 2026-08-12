<script setup lang="ts">
import { computed, h, withDirectives } from 'vue'
import type { VNode } from 'vue'
import { ExitOutline, PersonRemoveOutline } from '@vicons/ionicons5'
import { NButton, NDataTable, NEmpty, NIcon } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'

import { permissionDirective } from '@/directives'
import { useLocale } from '@/hooks'
import type { OnlineSession, OnlineSessionTableProps } from '@/types'
import { formatDateTime } from '@/utils'

defineOptions({ name: 'OnlineSessionTable' })

const props = defineProps<OnlineSessionTableProps>()
const emit = defineEmits<{
  'force-session': [session: OnlineSession]
  'force-user': [session: OnlineSession]
}>()

const { t } = useLocale()

const displayValue = (value: string | null): string => value || t('online.noValue')
const canForceUser = (session: OnlineSession): boolean =>
  typeof session.user_id === 'number' && Number.isInteger(session.user_id) && session.user_id > 0
const withForceLogoutPermission = (node: VNode): VNode =>
  withDirectives(node, [[permissionDirective, 'monitor:online:forceLogout']])

const renderActions = (session: OnlineSession): VNode => {
  if (!props.forceLogoutAllowed) {
    return h('span', t('online.noValue'))
  }

  const sessionAction = `session:${session.token_id}`
  const userAction = `user:${session.user_id}`
  const busy = props.revokingAction !== null

  const actions = [
    withForceLogoutPermission(
      h(
        NButton,
        {
          quaternary: true,
          circle: true,
          type: 'warning',
          loading: props.revokingAction === sessionAction,
          disabled: busy,
          'aria-label': t('online.action.forceSession'),
          title: t('online.action.forceSession'),
          onClick: () => emit('force-session', session),
        },
        { icon: () => h(NIcon, null, { default: () => h(ExitOutline) }) },
      ),
    ),
  ]

  if (canForceUser(session)) {
    actions.push(
      withForceLogoutPermission(
        h(
          NButton,
          {
            quaternary: true,
            circle: true,
            type: 'error',
            loading: props.revokingAction === userAction,
            disabled: busy,
            'aria-label': t('online.action.forceUser'),
            title: t('online.action.forceUser'),
            onClick: () => emit('force-user', session),
          },
          { icon: () => h(NIcon, null, { default: () => h(PersonRemoveOutline) }) },
        ),
      ),
    )
  }

  return h('div', { class: 'online-row-actions' }, actions)
}

const columns = computed<DataTableColumns<OnlineSession>>(() => {
  const dataColumns: DataTableColumns<OnlineSession> = [
    {
      title: t('online.column.username'),
      key: 'username',
      width: 150,
      ellipsis: { tooltip: true },
      render: (session) => displayValue(session.username),
    },
    {
      title: t('online.column.userId'),
      key: 'user_id',
      width: 110,
      render: (session) => String(session.user_id),
    },
    {
      title: t('online.column.ipAddress'),
      key: 'ip_address',
      width: 150,
      render: (session) => displayValue(session.ip_address),
    },
    {
      title: t('online.column.userAgent'),
      key: 'user_agent',
      minWidth: 300,
      ellipsis: { tooltip: true },
      render: (session) => displayValue(session.user_agent),
    },
    {
      title: t('online.column.loginTime'),
      key: 'login_time',
      width: 180,
      render: (session) => formatDateTime(session.login_time, { fallback: t('online.noValue') }),
    },
    {
      title: t('online.column.expireTime'),
      key: 'expire_time',
      width: 180,
      render: (session) => formatDateTime(session.expire_time, { fallback: t('online.noValue') }),
    },
  ]

  if (props.forceLogoutAllowed) {
    dataColumns.push({
      title: t('online.column.action'),
      key: 'action',
      width: 110,
      fixed: 'right',
      render: renderActions,
    })
  }

  return dataColumns
})

const rowKey = (session: OnlineSession): string => session.token_id
</script>

<template>
  <NDataTable
    :columns="columns"
    :data="props.data"
    :loading="props.loading"
    :scroll-x="1190"
    :row-key="rowKey"
    remote
  >
    <template #empty><NEmpty :description="t('online.empty')" /></template>
  </NDataTable>
</template>

<style lang="scss" scoped>
.online-row-actions {
  display: flex;
  align-items: center;
  gap: 2px;
}
</style>
