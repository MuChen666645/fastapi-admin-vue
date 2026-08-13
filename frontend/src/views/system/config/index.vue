<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { AddOutline, RefreshOutline } from '@vicons/ionicons5'
import { NAlert, NButton, NIcon, NPagination, useDialog, useMessage } from 'naive-ui'

import {
  createSystemConfig,
  deleteSystemConfig,
  fetchSystemConfigDetail,
  fetchSystemConfigs,
  updateSystemConfig,
} from '@/api'
import { useLocale, usePagination, usePermission } from '@/hooks'
import type {
  SystemConfig,
  SystemConfigActionPermissions,
  SystemConfigFilters,
  SystemConfigFormMode,
  SystemConfigFormModel,
} from '@/types'
import SystemConfigFormModal from './components/SystemConfigFormModal.vue'
import SystemConfigDetailModal from './components/SystemConfigDetailModal.vue'
import SystemConfigSearchPanel from './components/SystemConfigSearchPanel.vue'
import SystemConfigTable from './components/SystemConfigTable.vue'
import { createSystemConfigPayload, createSystemConfigUpdatePayload } from './payloads'

defineOptions({ name: 'SystemConfigView' })

const createInitialFilters = (): SystemConfigFilters => ({ name: '', key: '' })

const createInitialFormModel = (): SystemConfigFormModel => ({
  config_name: '',
  config_key: '',
  config_value: '',
  config_type: 'text',
  is_builtin: false,
  remark: '',
})

const { t } = useLocale()
const { hasPermission } = usePermission()
const dialog = useDialog()
const message = useMessage()

const permissions = computed<SystemConfigActionPermissions>(() => ({
  list: hasPermission('system:config:list'),
  query: hasPermission('system:config:query'),
  create: hasPermission('system:config:add'),
  edit: hasPermission('system:config:edit'),
  remove: hasPermission('system:config:remove'),
  removeBuiltin: hasPermission('*:*:*'),
}))

const filters = reactive<SystemConfigFilters>(createInitialFilters())
const initialFilters = createInitialFilters()
const formModel = reactive<SystemConfigFormModel>(createInitialFormModel())
const editingId = ref<number | null>(null)
const formLoading = ref(false)
const formMode = ref<SystemConfigFormMode>('create')
const formVisible = ref(false)
const detailItem = ref<SystemConfig | null>(null)
const detailVisible = ref(false)
const detailLoading = ref(false)

const pagination = usePagination((params) => fetchSystemConfigs(params, filters), {
  immediate: false,
  initialPageSize: 20,
  pageSizes: [20, 50, 100],
})

const totalLabel = computed(() =>
  t('systemConfig.total').replace('{count}', String(pagination.total.value)),
)
const pageInfo = computed(() =>
  t('systemConfig.pageInfo')
    .replace('{page}', String(pagination.page.value))
    .replace('{pageSize}', String(pagination.pageSize.value)),
)

const replaceFormModel = (model: SystemConfigFormModel): void => {
  Object.assign(formModel, model)
}

const createFormModelFromConfig = (item: SystemConfig): SystemConfigFormModel => ({
  config_name: item.config_name,
  config_key: item.config_key,
  config_value: item.config_value ?? '',
  config_type: item.config_type,
  is_builtin: item.is_builtin,
  remark: item.remark ?? '',
})

const refreshSystemConfigs = async (): Promise<void> => {
  if (!permissions.value.list) {
    return
  }

  await pagination.refresh()
}

const handleSearch = (nextFilters: SystemConfigFilters): void => {
  if (!permissions.value.list) {
    return
  }

  Object.assign(filters, nextFilters)
  void pagination.reset()
}

const handleReset = (nextFilters: SystemConfigFilters): void => {
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

const openEdit = (item: SystemConfig): void => {
  if (!permissions.value.edit) {
    return
  }

  formMode.value = 'edit'
  editingId.value = item.id
  replaceFormModel(createFormModelFromConfig(item))
  formVisible.value = true
}

const openDetail = async (item: SystemConfig): Promise<void> => {
  if (!permissions.value.query || detailLoading.value) {
    return
  }

  detailVisible.value = true
  detailLoading.value = true
  detailItem.value = null
  try {
    detailItem.value = await fetchSystemConfigDetail(item.id)
  } finally {
    detailLoading.value = false
  }
}

const saveSystemConfig = async (model: SystemConfigFormModel): Promise<void> => {
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
      await createSystemConfig(createSystemConfigPayload(model))
      message.success(t('systemConfig.form.createSuccess'))
    } else if (editingId.value !== null) {
      await updateSystemConfig(editingId.value, createSystemConfigUpdatePayload(model))
      message.success(t('systemConfig.form.updateSuccess'))
    } else {
      return
    }

    formVisible.value = false
    await refreshSystemConfigs()
  } finally {
    formLoading.value = false
  }
}

const confirmDelete = (item: SystemConfig): void => {
  if (!permissions.value.remove || (item.is_builtin && !permissions.value.removeBuiltin)) {
    return
  }

  dialog.warning({
    title: t('systemConfig.action.confirmDelete'),
    content: t('systemConfig.action.confirmDeleteContent'),
    positiveText: t('systemConfig.action.delete'),
    negativeText: t('systemConfig.form.cancel'),
    onPositiveClick: async () => {
      if (!permissions.value.remove || (item.is_builtin && !permissions.value.removeBuiltin)) {
        return
      }

      await deleteSystemConfig(item.id)
      message.success(t('systemConfig.form.deleteSuccess'))
      await refreshSystemConfigs()
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
  <main class="system-config-page">
    <section class="system-config-list-panel" aria-labelledby="system-config-list-title">
      <header class="system-config-list-heading">
        <div>
          <h2 id="system-config-list-title">{{ t('systemConfig.title') }}</h2>
          <p>{{ t('systemConfig.description') }}</p>
        </div>
        <div class="system-config-page-actions">
          <NButton
            v-if="permissions.create"
            v-permission="'system:config:add'"
            type="primary"
            @click="openCreate"
          >
            <template #icon>
              <NIcon><AddOutline /></NIcon>
            </template>
            {{ t('systemConfig.action.create') }}
          </NButton>
          <NButton
            v-if="permissions.list"
            v-permission="'system:config:list'"
            quaternary
            circle
            :loading="pagination.loading.value"
            :aria-label="t('systemConfig.refresh')"
            :title="t('systemConfig.refresh')"
            @click="refreshSystemConfigs"
          >
            <template #icon>
              <NIcon><RefreshOutline /></NIcon>
            </template>
          </NButton>
          <span class="system-config-total">{{ totalLabel }}</span>
        </div>
      </header>

      <SystemConfigSearchPanel
        :model="filters"
        :initial-values="initialFilters"
        :loading="pagination.loading.value"
        @search="handleSearch"
        @reset="handleReset"
      />

      <div v-if="pagination.error.value" class="system-config-page-error">
        <NAlert type="error" :show-icon="false">{{ t('systemConfig.loadFailed') }}</NAlert>
        <NButton
          v-if="permissions.list"
          v-permission="'system:config:list'"
          size="small"
          @click="refreshSystemConfigs"
        >
          {{ t('systemConfig.retry') }}
        </NButton>
      </div>

      <SystemConfigTable
        :data="pagination.data.value"
        :loading="pagination.loading.value"
        :permissions="permissions"
        @detail="openDetail"
        @edit="openEdit"
        @delete="confirmDelete"
      />

      <footer v-if="permissions.list" class="system-config-page-footer">
        <NPagination v-bind="pagination.pagination.value" />
        <span>{{ pageInfo }}</span>
      </footer>
    </section>

    <SystemConfigDetailModal
      v-model:show="detailVisible"
      :loading="detailLoading"
      :item="detailItem"
    />

    <SystemConfigFormModal
      v-model:show="formVisible"
      :mode="formMode"
      :model="formModel"
      :loading="formLoading"
      @submit="saveSystemConfig"
      @reset="resetForm"
    />
  </main>
</template>

<style lang="scss" scoped>
.system-config-page {
  display: grid;
  min-width: 0;
  gap: 16px;
  color: var(--app-color-text);
}

.system-config-list-panel {
  min-width: 0;
  padding: 20px 24px 0;
  overflow: hidden;
  border: 1px solid var(--app-color-border);
  border-radius: 8px;
  background: var(--app-color-surface);
}

.system-config-list-heading,
.system-config-page-actions,
.system-config-page-error,
.system-config-page-footer {
  display: flex;
  align-items: center;
  gap: 16px;
}

.system-config-list-heading {
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 16px;
}

.system-config-list-heading h2,
.system-config-list-heading p,
.system-config-total {
  margin: 0;
}

.system-config-list-heading h2 {
  font-size: 16px;
}

.system-config-list-heading p {
  margin-top: 6px;
  color: var(--app-color-text-muted);
  font-size: 13px;
  line-height: 1.5;
}

.system-config-page-actions {
  justify-content: flex-end;
  gap: 8px;
  flex-wrap: wrap;
}

.system-config-total,
.system-config-page-footer span {
  flex: 0 0 auto;
  color: var(--app-color-text-muted);
  font-size: 13px;
}

.system-config-page-error {
  margin: 16px 0;
}

.system-config-page-error .n-alert {
  flex: 1;
}

.system-config-page-footer {
  justify-content: space-between;
  min-height: 64px;
  padding: 12px 0;
  border-top: 1px solid var(--app-color-border);
}

.system-config-list-panel :deep(.app-search-form) {
  margin-bottom: 16px;
}

.system-config-list-panel :deep(.n-data-table) {
  margin: 16px 0;
}

@media (width <= 720px) {
  .system-config-list-heading {
    align-items: stretch;
    flex-direction: column;
  }

  .system-config-page-actions {
    justify-content: flex-start;
  }
}

@media (width <= 640px) {
  .system-config-list-panel {
    padding-right: 16px;
    padding-left: 16px;
  }

  .system-config-list-panel :deep(.n-data-table) {
    margin: 16px -16px 0;
  }

  .system-config-page-footer {
    align-items: flex-start;
    flex-direction: column-reverse;
  }
}
</style>
