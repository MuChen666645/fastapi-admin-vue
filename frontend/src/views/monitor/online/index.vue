<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { RefreshOutline } from '@vicons/ionicons5'
import { NAlert, NButton, NIcon, NPagination, useDialog, useMessage } from 'naive-ui'

import { fetchOnlineSessions, forceLogoutSession, forceLogoutUser } from '@/api'
import { useLocale, usePagination, usePermission } from '@/hooks'
import type { OnlineActionPermissions, OnlineSession, OnlineSessionFilters } from '@/types'
import OnlineSearchPanel from './components/OnlineSearchPanel.vue'
import OnlineSessionTable from './components/OnlineSessionTable.vue'

defineOptions({ name: 'MonitorOnlineView' })

const createInitialFilters = (): OnlineSessionFilters => ({ username: '', ip_address: '' })

const { t } = useLocale()
const { hasPermission } = usePermission()
const dialog = useDialog()
const message = useMessage()

const permissions = computed<OnlineActionPermissions>(() => ({
  list: hasPermission('monitor:online:list'),
  forceLogout: hasPermission('monitor:online:forceLogout'),
}))

const filters = reactive<OnlineSessionFilters>(createInitialFilters())
const initialFilters = createInitialFilters()
const revokingAction = ref<string | null>(null)

const pagination = usePagination((params) => fetchOnlineSessions(params, filters), {
  immediate: false,
  initialPageSize: 20,
  pageSizes: [20, 50, 100],
})

const totalLabel = computed(() =>
  t('online.total').replace('{count}', String(pagination.total.value)),
)
const pageInfo = computed(() =>
  t('online.pageInfo')
    .replace('{page}', String(pagination.page.value))
    .replace('{pageSize}', String(pagination.pageSize.value)),
)

const refreshOnlineSessions = async (): Promise<void> => {
  if (!permissions.value.list) {
    return
  }

  await pagination.refresh()
}

const handleSearch = (nextFilters: OnlineSessionFilters): void => {
  if (!permissions.value.list) {
    return
  }

  Object.assign(filters, nextFilters)
  void pagination.reset()
}

const handleReset = (nextFilters: OnlineSessionFilters): void => {
  if (!permissions.value.list) {
    return
  }

  Object.assign(filters, nextFilters)
  void pagination.reset()
}

const executeForceLogout = async (
  actionKey: string,
  request: () => Promise<unknown>,
  successMessage: string | null,
): Promise<void> => {
  if (!permissions.value.forceLogout || revokingAction.value !== null) {
    return
  }

  revokingAction.value = actionKey
  try {
    await request()
    if (successMessage) {
      message.success(successMessage)
    }
    await refreshOnlineSessions()
  } finally {
    revokingAction.value = null
  }
}

const confirmForceSession = (session: OnlineSession): void => {
  if (!permissions.value.forceLogout || revokingAction.value !== null) {
    return
  }

  dialog.warning({
    title: t('online.action.confirmSession'),
    content: t('online.action.confirmSessionContent').replace(
      '{username}',
      session.username ?? t('online.noValue'),
    ),
    positiveText: t('online.action.forceSession'),
    negativeText: t('online.action.cancel'),
    onPositiveClick: () =>
      executeForceLogout(
        `session:${session.token_id}`,
        () => forceLogoutSession(session.token_id),
        t('online.action.forceSessionSuccess'),
      ),
  })
}

const confirmForceUser = (session: OnlineSession): void => {
  if (
    !permissions.value.forceLogout ||
    revokingAction.value !== null ||
    typeof session.user_id !== 'number' ||
    !Number.isInteger(session.user_id) ||
    session.user_id <= 0
  ) {
    return
  }

  const userId = session.user_id
  dialog.warning({
    title: t('online.action.confirmUser'),
    content: t('online.action.confirmUserContent').replace(
      '{username}',
      session.username ?? String(userId),
    ),
    positiveText: t('online.action.forceUser'),
    negativeText: t('online.action.cancel'),
    onPositiveClick: async () => {
      if (!permissions.value.forceLogout) {
        return
      }

      await executeForceLogout(
        `user:${userId}`,
        async () => {
          const result = await forceLogoutUser(userId)
          message.success(
            t('online.action.forceUserSuccess').replace(
              '{count}',
              String(result.revoked_token_count),
            ),
          )
        },
        null,
      )
    },
  })
}

onMounted(() => {
  if (permissions.value.list) {
    void pagination.load()
  }
})
</script>

<template>
  <main class="online-page">
    <section class="online-list-panel" aria-labelledby="online-list-title">
      <header class="online-list-heading">
        <div>
          <h2 id="online-list-title">{{ t('online.title') }}</h2>
          <p>{{ t('online.description') }}</p>
        </div>
        <div class="online-page-actions">
          <NButton
            v-if="permissions.list"
            v-permission="'monitor:online:list'"
            quaternary
            circle
            :loading="pagination.loading.value"
            :aria-label="t('online.refresh')"
            :title="t('online.refresh')"
            @click="refreshOnlineSessions"
          >
            <template #icon>
              <NIcon><RefreshOutline /></NIcon>
            </template>
          </NButton>
          <span class="online-total">{{ totalLabel }}</span>
        </div>
      </header>

      <OnlineSearchPanel
        :model="filters"
        :initial-values="initialFilters"
        :loading="pagination.loading.value"
        @search="handleSearch"
        @reset="handleReset"
      />

      <div v-if="pagination.error.value" class="online-page-error">
        <NAlert type="error" :show-icon="false">{{ t('online.loadFailed') }}</NAlert>
        <NButton
          v-if="permissions.list"
          v-permission="'monitor:online:list'"
          size="small"
          @click="refreshOnlineSessions"
        >
          {{ t('online.retry') }}
        </NButton>
      </div>

      <OnlineSessionTable
        :data="pagination.data.value"
        :loading="pagination.loading.value"
        :force-logout-allowed="permissions.forceLogout"
        :revoking-action="revokingAction"
        @force-session="confirmForceSession"
        @force-user="confirmForceUser"
      />

      <footer v-if="permissions.list" class="online-page-footer">
        <NPagination v-bind="pagination.pagination.value" />
        <span>{{ pageInfo }}</span>
      </footer>
    </section>
  </main>
</template>

<style lang="scss" scoped>
.online-page {
  display: grid;
  min-width: 0;
  gap: 16px;
  color: var(--app-color-text);
}

.online-list-panel {
  min-width: 0;
  padding: 20px 24px 0;
  overflow: hidden;
  border: 1px solid var(--app-color-border);
  border-radius: 8px;
  background: var(--app-color-surface);
}

.online-list-heading,
.online-page-actions,
.online-page-error,
.online-page-footer {
  display: flex;
  align-items: center;
  gap: 16px;
}

.online-list-heading {
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 16px;
}

.online-list-heading h2,
.online-list-heading p,
.online-total {
  margin: 0;
}

.online-list-heading h2 {
  font-size: 16px;
}

.online-list-heading p {
  margin-top: 6px;
  color: var(--app-color-text-muted);
  font-size: 13px;
  line-height: 1.5;
}

.online-page-actions {
  justify-content: flex-end;
  gap: 8px;
  flex-wrap: wrap;
}

.online-total,
.online-page-footer span {
  flex: 0 0 auto;
  color: var(--app-color-text-muted);
  font-size: 13px;
}

.online-page-error {
  margin: 16px 0;
}

.online-page-error .n-alert {
  flex: 1;
}

.online-page-footer {
  justify-content: space-between;
  min-height: 64px;
  padding: 12px 0;
  border-top: 1px solid var(--app-color-border);
}

.online-list-panel :deep(.app-search-form) {
  margin-bottom: 16px;
}

.online-list-panel :deep(.n-data-table) {
  margin: 16px 0;
}

@media (width <= 720px) {
  .online-list-heading {
    align-items: stretch;
    flex-direction: column;
  }

  .online-page-actions {
    justify-content: flex-start;
  }
}

@media (width <= 640px) {
  .online-list-panel {
    padding-right: 16px;
    padding-left: 16px;
  }

  .online-list-panel :deep(.n-data-table) {
    margin: 16px -16px 0;
  }

  .online-page-footer {
    align-items: flex-start;
    flex-direction: column-reverse;
  }
}
</style>
