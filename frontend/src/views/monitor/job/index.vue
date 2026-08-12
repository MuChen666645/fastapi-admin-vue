<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { NAlert, NButton, NPagination, useDialog, useMessage } from 'naive-ui'

import {
  createScheduledJob,
  deleteScheduledJob,
  fetchScheduledJobDetail,
  fetchScheduledJobLogs,
  fetchScheduledJobs,
  runScheduledJob,
  updateScheduledJob,
} from '@/api'
import { useLocale, usePagination, usePermission } from '@/hooks'
import type {
  ScheduledJob,
  ScheduledJobActionPermissions,
  ScheduledJobFilters,
  ScheduledJobFormMode,
  ScheduledJobFormModel,
  ScheduledJobRunResult,
} from '@/types'
import JobDetailModal from './components/JobDetailModal.vue'
import JobFormModal from './components/JobFormModal.vue'
import JobLogModal from './components/JobLogModal.vue'
import JobPageHeader from './components/JobPageHeader.vue'
import JobSearchPanel from './components/JobSearchPanel.vue'
import JobTable from './components/JobTable.vue'
import {
  calculateScheduledJobRunTimeout,
  createScheduledJobPayload,
  createScheduledJobUpdatePayload,
} from './payloads'
import { getJobExecutionStatusLabel } from './presentation'

defineOptions({ name: 'MonitorJobView' })

const createInitialFilters = (): ScheduledJobFilters => ({ name: '', status: null })
const createInitialFormModel = (): ScheduledJobFormModel => ({
  job_name: '',
  job_key: '',
  task_name: '',
  cron_expression: '0 * * * *',
  args_json: '{}',
  timeout_seconds: 300,
  max_retries: 0,
  status: '1',
})

const { t } = useLocale()
const { hasPermission } = usePermission()
const dialog = useDialog()
const message = useMessage()

const permissions = computed<ScheduledJobActionPermissions>(() => ({
  list: hasPermission('monitor:job:list'),
  query: hasPermission('monitor:job:query'),
  create: hasPermission('monitor:job:add'),
  edit: hasPermission('monitor:job:edit'),
  remove: hasPermission('monitor:job:remove'),
  run: hasPermission('monitor:job:run'),
}))

const filters = reactive<ScheduledJobFilters>(createInitialFilters())
const initialFilters = createInitialFilters()
const formModel = reactive<ScheduledJobFormModel>(createInitialFormModel())
const formMode = ref<ScheduledJobFormMode>('create')
const formVisible = ref(false)
const formLoading = ref(false)
const editingId = ref<number | null>(null)
const detailItem = ref<ScheduledJob | null>(null)
const detailVisible = ref(false)
const detailLoading = ref(false)
const logJob = ref<ScheduledJob | null>(null)
const logVisible = ref(false)
const processingAction = ref<string | null>(null)

const pagination = usePagination((params) => fetchScheduledJobs(params, filters), {
  immediate: false,
  initialPageSize: 20,
  pageSizes: [20, 50, 100],
})

const logPagination = usePagination(
  (params) => {
    if (!logJob.value) {
      throw new Error('未选择定时任务')
    }

    return fetchScheduledJobLogs(logJob.value.id, params)
  },
  {
    immediate: false,
    initialPageSize: 20,
    pageSizes: [20, 50, 100],
  },
)

const totalLabel = computed(() => t('job.total').replace('{count}', String(pagination.total.value)))
const pageInfo = computed(() =>
  t('job.pageInfo')
    .replace('{page}', String(pagination.page.value))
    .replace('{pageSize}', String(pagination.pageSize.value)),
)

const replaceFormModel = (model: ScheduledJobFormModel): void => {
  Object.assign(formModel, model)
}

const createFormModelFromJob = (item: ScheduledJob): ScheduledJobFormModel => ({
  job_name: item.job_name,
  job_key: item.job_key,
  task_name: item.task_name,
  cron_expression: item.cron_expression,
  args_json: item.args_json,
  timeout_seconds: item.timeout_seconds,
  max_retries: item.max_retries,
  status: item.status,
})

const refreshJobList = async (): Promise<void> => {
  if (!permissions.value.list) {
    return
  }

  await pagination.refresh()
}

const handleSearch = (nextFilters: ScheduledJobFilters): void => {
  if (!permissions.value.list) {
    return
  }

  Object.assign(filters, nextFilters)
  void pagination.reset()
}

const handleReset = (nextFilters: ScheduledJobFilters): void => {
  if (!permissions.value.list) {
    return
  }

  Object.assign(filters, nextFilters)
  void pagination.reset()
}

const openCreate = (): void => {
  if (!permissions.value.create) {
    return
  }

  formMode.value = 'create'
  editingId.value = null
  replaceFormModel(createInitialFormModel())
  formVisible.value = true
}

const openEdit = (item: ScheduledJob): void => {
  if (!permissions.value.edit || processingAction.value !== null) {
    return
  }

  formMode.value = 'edit'
  editingId.value = item.id
  replaceFormModel(createFormModelFromJob(item))
  formVisible.value = true
}

const openDetail = async (item: ScheduledJob): Promise<void> => {
  if (!permissions.value.query || processingAction.value !== null || detailLoading.value) {
    return
  }

  detailVisible.value = true
  detailLoading.value = true
  detailItem.value = null
  try {
    detailItem.value = await fetchScheduledJobDetail(item.id)
  } finally {
    detailLoading.value = false
  }
}

const openLogs = (item: ScheduledJob): void => {
  if (!permissions.value.query || processingAction.value !== null) {
    return
  }

  logJob.value = item
  logVisible.value = true
  void logPagination.reset()
}

const handleLogVisibility = (show: boolean): void => {
  logVisible.value = show
  if (!show) {
    void logPagination.reset({ reload: false })
  }
}

const saveJob = async (model: ScheduledJobFormModel): Promise<void> => {
  if (formLoading.value) {
    return
  }

  const canSave = formMode.value === 'create' ? permissions.value.create : permissions.value.edit
  if (!canSave) {
    return
  }

  formLoading.value = true
  try {
    if (formMode.value === 'create') {
      await createScheduledJob(createScheduledJobPayload(model))
      message.success(t('job.action.createSuccess'))
    } else if (editingId.value !== null) {
      await updateScheduledJob(editingId.value, createScheduledJobUpdatePayload(model))
      message.success(t('job.action.updateSuccess'))
    } else {
      return
    }

    formVisible.value = false
    await refreshJobList()
  } finally {
    formLoading.value = false
  }
}

const showRunResult = (result: ScheduledJobRunResult): void => {
  const status = getJobExecutionStatusLabel(result.status, t)
  const content = t('job.action.runResult')
    .replace('{status}', status)
    .replace('{message}', result.message ?? t('job.noValue'))

  switch (result.status) {
    case 'success':
      message.success(content)
      break
    case 'failed':
      message.error(content)
      break
    case 'skipped':
      message.warning(content)
      break
    default:
      message.info(content)
  }
}

const confirmRun = (item: ScheduledJob): void => {
  if (!permissions.value.run || item.status !== '1' || processingAction.value !== null) {
    return
  }

  dialog.warning({
    title: t('job.action.confirmRun'),
    content: t('job.action.confirmRunContent').replace('{name}', item.job_name),
    positiveText: t('job.action.run'),
    negativeText: t('job.action.cancel'),
    onPositiveClick: async () => {
      if (!permissions.value.run || item.status !== '1' || processingAction.value !== null) {
        return
      }

      processingAction.value = `run:${item.id}`
      try {
        const result = await runScheduledJob(
          item.id,
          calculateScheduledJobRunTimeout(item.timeout_seconds, item.max_retries),
        )
        showRunResult(result)
        await refreshJobList()
      } finally {
        processingAction.value = null
      }
    },
  })
}

const confirmDelete = (item: ScheduledJob): void => {
  if (!permissions.value.remove || processingAction.value !== null) {
    return
  }

  dialog.warning({
    title: t('job.action.confirmDelete'),
    content: t('job.action.confirmDeleteContent').replace('{name}', item.job_name),
    positiveText: t('job.action.delete'),
    negativeText: t('job.action.cancel'),
    onPositiveClick: async () => {
      if (!permissions.value.remove || processingAction.value !== null) {
        return
      }

      processingAction.value = `delete:${item.id}`
      try {
        await deleteScheduledJob(item.id)
        message.success(t('job.action.deleteSuccess'))
        await refreshJobList()
      } finally {
        processingAction.value = null
      }
    },
  })
}

const resetForm = (): void => {
  replaceFormModel(createInitialFormModel())
  editingId.value = null
  formMode.value = 'create'
}

onMounted(() => {
  if (permissions.value.list) {
    void pagination.load()
  }
})
</script>

<template>
  <main class="job-page">
    <section class="job-list-panel" aria-labelledby="job-list-title">
      <JobPageHeader
        :title="t('job.title')"
        :description="t('job.description')"
        :total="totalLabel"
        :refresh-loading="pagination.loading.value"
        :permissions="permissions"
        @create="openCreate"
        @refresh="refreshJobList"
      />

      <JobSearchPanel
        :model="filters"
        :initial-values="initialFilters"
        :loading="pagination.loading.value"
        @search="handleSearch"
        @reset="handleReset"
      />

      <div v-if="pagination.error.value" class="job-page-error">
        <NAlert type="error" :show-icon="false">{{ t('job.loadFailed') }}</NAlert>
        <NButton
          v-if="permissions.list"
          v-permission="'monitor:job:list'"
          size="small"
          @click="refreshJobList"
        >
          {{ t('job.retry') }}
        </NButton>
      </div>

      <JobTable
        :data="pagination.data.value"
        :loading="pagination.loading.value"
        :permissions="permissions"
        :processing-action="processingAction"
        @detail="openDetail"
        @edit="openEdit"
        @run="confirmRun"
        @logs="openLogs"
        @delete="confirmDelete"
      />

      <footer v-if="permissions.list" class="job-page-footer">
        <NPagination v-bind="pagination.pagination.value" />
        <span>{{ pageInfo }}</span>
      </footer>
    </section>

    <JobDetailModal v-model:show="detailVisible" :loading="detailLoading" :item="detailItem" />
    <JobFormModal
      v-model:show="formVisible"
      :mode="formMode"
      :model="formModel"
      :loading="formLoading"
      @submit="saveJob"
      @reset="resetForm"
    />
    <JobLogModal
      :show="logVisible"
      :job="logJob"
      :data="
        logPagination.loading.value || logPagination.error.value ? [] : logPagination.data.value
      "
      :loading="logPagination.loading.value"
      :has-error="logPagination.error.value !== null"
      :pagination="logPagination.pagination.value"
      @update:show="handleLogVisibility"
      @refresh="logPagination.refresh"
    />
  </main>
</template>

<style lang="scss" scoped>
.job-page {
  display: grid;
  min-width: 0;
  gap: 16px;
  color: var(--app-color-text);
}

.job-list-panel {
  min-width: 0;
  padding: 20px 24px 0;
  overflow: hidden;
  border: 1px solid var(--app-color-border);
  border-radius: 8px;
  background: var(--app-color-surface);
}

.job-page-error,
.job-page-footer {
  display: flex;
  align-items: center;
  gap: 16px;
}

.job-page-error {
  margin: 16px 0;
}

.job-page-error .n-alert {
  flex: 1;
}

.job-page-footer {
  justify-content: space-between;
  min-height: 64px;
  padding: 12px 0;
  border-top: 1px solid var(--app-color-border);
}

.job-page-footer span {
  flex: 0 0 auto;
  color: var(--app-color-text-muted);
  font-size: 13px;
}

.job-list-panel :deep(.app-search-form) {
  margin-bottom: 16px;
}

.job-list-panel :deep(.n-data-table) {
  margin: 16px 0;
}

@media (width <= 640px) {
  .job-list-panel {
    padding-right: 16px;
    padding-left: 16px;
  }

  .job-list-panel :deep(.n-data-table) {
    margin: 16px -16px 0;
  }

  .job-page-footer {
    align-items: flex-start;
    flex-direction: column-reverse;
  }
}
</style>
