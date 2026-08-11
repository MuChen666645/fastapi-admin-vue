<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { NAlert, NButton, NEmpty, NPagination, useDialog, useMessage } from 'naive-ui'

import { deleteLogs, fetchLogList } from '@/api'
import { useLocale, usePagination, usePermission } from '@/hooks'
import type { LogActionPermissions, LogListFilters, LogListItem, LogType } from '@/types'
import LogBatchActions from './components/LogBatchActions.vue'
import LogDetailModal from './components/LogDetailModal.vue'
import LogPageHeader from './components/LogPageHeader.vue'
import LogSearchPanel from './components/LogSearchPanel.vue'
import LogTable from './components/LogTable.vue'

defineOptions({ name: 'MonitorLogView' })

const createInitialFilters = (): LogListFilters => ({
  username: '',
  status: null,
  path: '',
  time_range: null,
})

const { t } = useLocale()
const { hasPermission } = usePermission()
const dialog = useDialog()
const message = useMessage()

const permissions = computed<LogActionPermissions>(() => ({
  loginList: hasPermission('monitor:login:list'),
  operationList: hasPermission('monitor:operation:list'),
  exceptionList: hasPermission('monitor:exception:list'),
  remove: hasPermission('monitor:log:remove'),
}))

const activeType = ref<LogType>('login')
const filters = reactive<LogListFilters>(createInitialFilters())
const appliedFilters = reactive<LogListFilters>(createInitialFilters())
const initialFilters = createInitialFilters()
const selectedIds = ref<number[]>([])
const deleteLoading = ref(false)
const detailItem = ref<LogListItem | null>(null)
const detailVisible = ref(false)

const hasListPermission = (type: LogType): boolean => {
  if (type === 'login') {
    return permissions.value.loginList
  }

  if (type === 'operation') {
    return permissions.value.operationList
  }

  return permissions.value.exceptionList
}

const availableTypes = computed<LogType[]>(() => {
  const types: LogType[] = []
  if (permissions.value.loginList) {
    types.push('login')
  }
  if (permissions.value.operationList) {
    types.push('operation')
  }
  if (permissions.value.exceptionList) {
    types.push('exception')
  }
  return types
})

const canListActiveType = computed(() => hasListPermission(activeType.value))

const activeListPermission = computed(() => {
  if (activeType.value === 'login') {
    return 'monitor:login:list'
  }

  if (activeType.value === 'operation') {
    return 'monitor:operation:list'
  }

  return 'monitor:exception:list'
})

const pagination = usePagination(
  (params) => fetchLogList(activeType.value, params, appliedFilters),
  {
    immediate: false,
    initialPageSize: 20,
    pageSizes: [20, 50, 100],
  },
)

const totalLabel = computed(() => t('log.total').replace('{count}', String(pagination.total.value)))
const pageInfo = computed(() =>
  t('log.pageInfo')
    .replace('{page}', String(pagination.page.value))
    .replace('{pageSize}', String(pagination.pageSize.value)),
)

const clearSelection = (): void => {
  selectedIds.value = []
}

const resetLogFilters = (): void => {
  Object.assign(filters, createInitialFilters())
  Object.assign(appliedFilters, createInitialFilters())
}

const refreshLogList = async (): Promise<void> => {
  if (!canListActiveType.value) {
    return
  }

  clearSelection()
  await pagination.refresh()
}

const changeActiveType = (nextType: LogType): void => {
  if (availableTypes.value.includes(nextType)) {
    activeType.value = nextType
  }
}

const handleSearch = (nextFilters: LogListFilters): void => {
  if (!canListActiveType.value) {
    return
  }

  Object.assign(appliedFilters, nextFilters)
  clearSelection()
  void pagination.reset()
}

const handleReset = (nextFilters: LogListFilters): void => {
  if (!canListActiveType.value) {
    return
  }

  Object.assign(appliedFilters, nextFilters)
  clearSelection()
  void pagination.reset()
}

const handleSelectedRowKeys = (keys: number[]): void => {
  selectedIds.value = keys
}

const openDetail = (item: LogListItem): void => {
  if (!canListActiveType.value) {
    return
  }

  detailItem.value = item
  detailVisible.value = true
}

const confirmDelete = (): void => {
  if (!permissions.value.remove || selectedIds.value.length === 0 || deleteLoading.value) {
    return
  }

  const ids = [...selectedIds.value]
  dialog.warning({
    title: t('log.action.confirmDelete'),
    content: t('log.action.confirmDeleteContent').replace('{count}', String(ids.length)),
    positiveText: t('log.action.deleteSelected'),
    negativeText: t('log.action.cancel'),
    onPositiveClick: async () => {
      if (!permissions.value.remove || ids.length === 0 || deleteLoading.value) {
        return
      }

      deleteLoading.value = true
      try {
        await deleteLogs(activeType.value, { ids })
        message.success(t('log.action.deleteSuccess'))
        clearSelection()
        await pagination.refresh()
      } finally {
        deleteLoading.value = false
      }
    },
  })
}

watch(
  availableTypes,
  (types) => {
    if (!types.includes(activeType.value)) {
      activeType.value = types.at(0) ?? 'login'
    }
  },
  { immediate: true },
)

watch(activeType, () => {
  clearSelection()
  resetLogFilters()
  detailVisible.value = false
  detailItem.value = null
  if (canListActiveType.value) {
    void pagination.reset()
    return
  }

  void pagination.reset({ reload: false })
})

onMounted(() => {
  if (canListActiveType.value) {
    void pagination.load()
  }
})
</script>

<template>
  <main class="log-page">
    <section class="log-list-panel" aria-labelledby="log-list-title">
      <LogPageHeader
        :available-types="availableTypes"
        :active-type="activeType"
        :total="totalLabel"
        :refresh-loading="pagination.loading.value"
        @update:active-type="changeActiveType"
        @refresh="refreshLogList"
      />

      <template v-if="canListActiveType">
        <LogSearchPanel
          :model="filters"
          :initial-values="initialFilters"
          :loading="pagination.loading.value"
          :active-type="activeType"
          @search="handleSearch"
          @reset="handleReset"
        />

        <LogBatchActions
          :selected-count="selectedIds.length"
          :loading="deleteLoading"
          :disabled="!permissions.remove"
          @remove="confirmDelete"
        />

        <div v-if="pagination.error.value" class="log-page-error">
          <NAlert type="error" :show-icon="false">{{ t('log.loadFailed') }}</NAlert>
          <NButton v-permission="activeListPermission" size="small" @click="refreshLogList">
            {{ t('log.retry') }}
          </NButton>
        </div>

        <LogTable
          :kind="activeType"
          :data="pagination.data.value"
          :loading="pagination.loading.value"
          :selected-row-keys="selectedIds"
          @detail="openDetail"
          @update:selected-row-keys="handleSelectedRowKeys"
        />

        <footer class="log-page-footer">
          <NPagination v-bind="pagination.pagination.value" />
          <span>{{ pageInfo }}</span>
        </footer>
      </template>

      <NEmpty v-else :description="t('log.noPermission')" />
    </section>

    <LogDetailModal v-model:show="detailVisible" :kind="activeType" :item="detailItem" />
  </main>
</template>

<style lang="scss" scoped>
.log-page {
  display: grid;
  min-width: 0;
  gap: 16px;
  color: var(--app-color-text);
}

.log-list-panel {
  min-width: 0;
  padding: 20px 24px 0;
  overflow: hidden;
  border: 1px solid var(--app-color-border);
  border-radius: 8px;
  background: var(--app-color-surface);
}

.log-page-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  min-height: 64px;
  padding: 12px 0;
  border-top: 1px solid var(--app-color-border);
}

.log-page-footer span {
  flex: 0 0 auto;
  color: var(--app-color-text-muted);
  font-size: 13px;
}

.log-list-panel :deep(.app-search-form) {
  margin-bottom: 16px;
}

.log-list-panel :deep(.n-data-table) {
  margin: 16px 0;
}

.log-page-error {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 16px 0;
}

.log-page-error .n-alert {
  flex: 1;
}

@media (width <= 640px) {
  .log-list-panel {
    padding-right: 16px;
    padding-left: 16px;
  }

  .log-list-panel :deep(.n-data-table) {
    margin: 16px -16px 0;
  }

  .log-page-footer {
    align-items: flex-start;
    flex-direction: column-reverse;
  }
}
</style>
