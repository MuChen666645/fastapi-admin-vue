<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { NAlert, NButton, NPagination, useDialog, useMessage } from 'naive-ui'

import {
  createRole,
  deleteRole,
  fetchDepartmentOptions,
  fetchMenuList,
  fetchRoleDetail,
  fetchRoleList,
  updateRole,
} from '@/api'
import { useLocale, usePagination } from '@/hooks'
import type {
  DepartmentOption,
  MenuItem,
  RoleDetail,
  RoleFormMode,
  RoleFormModel,
  RoleListFilters,
  RoleListItem,
} from '@/types'
import { isProtectedAdminRole } from '@/utils'
import RoleBatchActions from './components/RoleBatchActions.vue'
import RoleDetailModal from './components/RoleDetailModal.vue'
import RoleFormModal from './components/RoleFormModal.vue'
import RolePageHeader from './components/RolePageHeader.vue'
import RoleSearchPanel from './components/RoleSearchPanel.vue'
import RoleTable from './components/RoleTable.vue'
import { createRolePayload, createRoleUpdatePayload } from './payloads'
import { useRoleBatchActions } from './useRoleBatchActions'
import { useRoleFileActions } from './useRoleFileActions'

defineOptions({ name: 'SystemRoleView' })

const createInitialFilters = (): RoleListFilters => ({ name: '', code: '' })

const createInitialFormModel = (): RoleFormModel => ({
  name: '',
  code: '',
  description: '',
  data_scope: '5',
  status: '1',
  menu_ids: [],
  dept_ids: [],
  version: null,
})

const { t } = useLocale()
const dialog = useDialog()
const message = useMessage()
const filters = reactive<RoleListFilters>(createInitialFilters())
const initialFilters = createInitialFilters()
const formModel = reactive<RoleFormModel>(createInitialFormModel())
const menus = ref<MenuItem[]>([])
const departments = ref<DepartmentOption[]>([])
const detailItem = ref<RoleDetail | null>(null)
const detailLoading = ref(false)
const detailVisible = ref(false)
const editTarget = ref<RoleListItem | null>(null)
const formLoading = ref(false)
const formMode = ref<RoleFormMode>('create')
const formVisible = ref(false)
const selectedRoleIds = ref<number[]>([])
const optionsLoaded = ref(false)

const pagination = usePagination((params) => fetchRoleList(params, filters), {
  initialPageSize: 20,
  pageSizes: [20, 50, 100],
})

const totalLabel = computed(() =>
  t('role.total').replace('{count}', String(pagination.total.value)),
)

const pageInfo = computed(() =>
  t('message.pageInfo')
    .replace('{page}', String(pagination.page.value))
    .replace('{pageSize}', String(pagination.pageSize.value)),
)

const clearSelection = (): void => {
  selectedRoleIds.value = []
}

const refreshRoleList = async (): Promise<void> => {
  clearSelection()
  await pagination.refresh()
}

const { batchLoading, confirmStatus, handleSelectionChange } = useRoleBatchActions({
  refresh: refreshRoleList,
  selectedRoleIds,
})
const { exportLoading, handleExport, handleImport, importLoading } = useRoleFileActions({
  refresh: refreshRoleList,
})

const replaceFormModel = (model: RoleFormModel): void => {
  Object.assign(formModel, model)
}

const createFormModelFromRole = (item: RoleListItem): RoleFormModel => ({
  ...createInitialFormModel(),
  name: item.name,
  code: item.code,
  description: item.description ?? '',
  data_scope: item.data_scope,
  status: item.status,
  version: item.version,
})

const handleSearch = (nextFilters: RoleListFilters): void => {
  Object.assign(filters, nextFilters)
  clearSelection()
  void pagination.reset()
}

const handleReset = (nextFilters: RoleListFilters): void => {
  Object.assign(filters, nextFilters)
  clearSelection()
  void pagination.reset()
}

const refreshList = (): void => {
  void refreshRoleList()
}

const loadOptions = async (): Promise<void> => {
  if (optionsLoaded.value) {
    return
  }

  await Promise.allSettled([
    fetchMenuList().then((items) => {
      menus.value = items
    }),
    fetchDepartmentOptions().then((items) => {
      departments.value = items
    }),
  ])
  optionsLoaded.value = true
}

const openCreate = async (): Promise<void> => {
  formMode.value = 'create'
  editTarget.value = null
  replaceFormModel(createInitialFormModel())
  formVisible.value = true
  formLoading.value = true
  try {
    await loadOptions()
  } finally {
    formLoading.value = false
  }
}

const openDetail = async (item: RoleListItem): Promise<void> => {
  detailVisible.value = true
  detailLoading.value = true
  detailItem.value = null
  try {
    detailItem.value = await fetchRoleDetail(item.id)
  } finally {
    detailLoading.value = false
  }
}

const openEdit = async (item: RoleListItem): Promise<void> => {
  if (isProtectedAdminRole(item.code)) {
    return
  }

  formMode.value = 'edit'
  editTarget.value = item
  replaceFormModel(createFormModelFromRole(item))
  formVisible.value = true
  formLoading.value = true
  try {
    const [detail] = await Promise.all([fetchRoleDetail(item.id), loadOptions()])
    replaceFormModel({
      ...createFormModelFromRole(detail),
      menu_ids: detail.menu_ids,
      dept_ids: detail.dept_ids,
    })
  } finally {
    formLoading.value = false
  }
}

const saveRole = async (model: RoleFormModel): Promise<void> => {
  if (formLoading.value) {
    return
  }

  formLoading.value = true
  try {
    if (formMode.value === 'create') {
      await createRole(createRolePayload(model))
      message.success(t('role.form.createSuccess'))
    } else if (editTarget.value && !isProtectedAdminRole(editTarget.value.code)) {
      await updateRole(editTarget.value.id, createRoleUpdatePayload(model))
      message.success(t('role.form.updateSuccess'))
    } else {
      return
    }

    formVisible.value = false
    await pagination.refresh()
  } finally {
    formLoading.value = false
  }
}

const confirmDelete = (item: RoleListItem): void => {
  if (isProtectedAdminRole(item.code)) {
    return
  }

  dialog.warning({
    title: t('role.action.confirmDelete'),
    content: t('role.action.confirmDeleteContent'),
    positiveText: t('role.action.delete'),
    negativeText: t('role.form.cancel'),
    onPositiveClick: async () => {
      if (isProtectedAdminRole(item.code)) {
        return
      }
      await deleteRole(item.id)
      message.success(t('role.form.deleteSuccess'))
      await refreshRoleList()
    },
  })
}

const resetForm = (): void => {
  replaceFormModel(createInitialFormModel())
  editTarget.value = null
  formMode.value = 'create'
}
</script>

<template>
  <main class="role-page">
    <section class="role-list-panel" aria-labelledby="role-list-title">
      <RolePageHeader
        :title="t('role.title')"
        :description="t('role.description')"
        :total="totalLabel"
        :refresh-loading="pagination.loading.value"
        :export-loading="exportLoading"
        :import-loading="importLoading"
        @create="openCreate"
        @refresh="refreshList"
        @export="handleExport"
        @import="handleImport"
      />
      <RoleSearchPanel
        :model="filters"
        :initial-values="initialFilters"
        :loading="pagination.loading.value"
        @search="handleSearch"
        @reset="handleReset"
      />
      <RoleBatchActions
        :selected-count="selectedRoleIds.length"
        :loading="batchLoading"
        @status="confirmStatus"
      />
      <div v-if="pagination.error.value" class="role-page-error">
        <NAlert type="error" :show-icon="false">{{ t('role.loadFailed') }}</NAlert>
        <NButton v-permission="'system:role:list'" size="small" @click="refreshList">
          {{ t('role.retry') }}
        </NButton>
      </div>
      <RoleTable
        :data="pagination.data.value"
        :loading="pagination.loading.value"
        :selected-row-keys="selectedRoleIds"
        @detail="openDetail"
        @edit="openEdit"
        @delete="confirmDelete"
        @update:selected-row-keys="handleSelectionChange"
      />
      <footer class="role-page-footer">
        <NPagination v-bind="pagination.pagination.value" />
        <span>{{ pageInfo }}</span>
      </footer>
    </section>

    <RoleDetailModal v-model:show="detailVisible" :loading="detailLoading" :item="detailItem" />
    <RoleFormModal
      v-model:show="formVisible"
      :mode="formMode"
      :model="formModel"
      :loading="formLoading"
      :menus="menus"
      :departments="departments"
      @submit="saveRole"
      @reset="resetForm"
    />
  </main>
</template>

<style lang="scss" scoped>
.role-page {
  display: grid;
  min-width: 0;
  gap: 16px;
  color: var(--app-color-text);
}

.role-list-panel {
  min-width: 0;
  padding: 20px 24px 0;
  overflow: hidden;
  border: 1px solid var(--app-color-border);
  border-radius: 8px;
  background: var(--app-color-surface);
}

.role-page-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  min-height: 64px;
  padding: 12px 0;
  border-top: 1px solid var(--app-color-border);
}

.role-page-footer span {
  flex: 0 0 auto;
  color: var(--app-color-text-muted);
  font-size: 13px;
}

.role-list-panel :deep(.app-search-form) {
  margin-bottom: 16px;
}

.role-list-panel :deep(.n-data-table) {
  margin: 16px 0;
}

.role-page-error {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 16px 0;
}

.role-page-error .n-alert {
  flex: 1;
}

@media (width <= 640px) {
  .role-list-panel {
    padding-right: 16px;
    padding-left: 16px;
  }

  .role-list-panel :deep(.n-data-table) {
    margin: 16px -16px 0;
  }

  .role-page-footer {
    align-items: flex-start;
    flex-direction: column-reverse;
  }
}
</style>
