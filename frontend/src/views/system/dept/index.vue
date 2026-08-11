<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { NAlert, NButton, useDialog, useMessage } from 'naive-ui'

import {
  createDepartment,
  deleteDepartment,
  fetchDepartmentDetail,
  fetchDepartmentList,
  updateDepartment,
} from '@/api'
import { useLocale, usePermission } from '@/hooks'
import type {
  DepartmentActionPermissions,
  DepartmentDetail,
  DepartmentFormMode,
  DepartmentFormModel,
  DepartmentListFilters,
  DepartmentListItem,
} from '@/types'
import DepartmentDetailModal from './components/DepartmentDetailModal.vue'
import DepartmentFormModal from './components/DepartmentFormModal.vue'
import DepartmentPageHeader from './components/DepartmentPageHeader.vue'
import DepartmentSearchPanel from './components/DepartmentSearchPanel.vue'
import DepartmentTable from './components/DepartmentTable.vue'
import { createDepartmentPayload, createDepartmentUpdatePayload } from './payloads'

defineOptions({ name: 'SystemDeptView' })

const createInitialFilters = (): DepartmentListFilters => ({ name: '', status: null })

const createInitialFormModel = (): DepartmentFormModel => ({
  parent_id: 0,
  dept_name: '',
  order_num: 0,
  leader: '',
  phone: '',
  email: '',
  status: '1',
})

const { t } = useLocale()
const { hasPermission } = usePermission()
const dialog = useDialog()
const message = useMessage()

const permissions = computed<DepartmentActionPermissions>(() => ({
  list: hasPermission('system:dept:list'),
  query: hasPermission('system:dept:query'),
  create: hasPermission('system:dept:add'),
  edit: hasPermission('system:dept:edit'),
  remove: hasPermission('system:dept:remove'),
}))

const filters = reactive<DepartmentListFilters>(createInitialFilters())
const initialFilters = createInitialFilters()
const formModel = reactive<DepartmentFormModel>(createInitialFormModel())
const departments = ref<DepartmentListItem[]>([])
const allDepartments = ref<DepartmentListItem[]>([])
const listLoading = ref(false)
const listError = ref('')
const departmentOptionsLoaded = ref(false)
const detailItem = ref<DepartmentDetail | null>(null)
const detailLoading = ref(false)
const detailParentName = ref('')
const detailVisible = ref(false)
const editingId = ref<number | null>(null)
const formLoading = ref(false)
const formMode = ref<DepartmentFormMode>('create')
const formVisible = ref(false)
let listRequestId = 0

const hasActiveFilters = (): boolean => filters.name.trim() !== '' || filters.status !== null

const flattenDepartments = (items: DepartmentListItem[]): DepartmentListItem[] =>
  items.flatMap((item) => [item, ...flattenDepartments(item.children)])

const totalLabel = computed(() =>
  t('department.total').replace('{count}', String(flattenDepartments(departments.value).length)),
)

const departmentNames = computed<Record<number, string>>(() =>
  flattenDepartments(allDepartments.value).reduce<Record<number, string>>((names, item) => {
    names[item.dept_id] = item.dept_name
    return names
  }, {}),
)

const replaceFormModel = (model: DepartmentFormModel): void => {
  Object.assign(formModel, model)
}

const createFormModelFromDepartment = (item: DepartmentListItem): DepartmentFormModel => ({
  parent_id: item.parent_id ?? 0,
  dept_name: item.dept_name,
  order_num: item.order_num,
  leader: item.leader ?? '',
  phone: item.phone ?? '',
  email: item.email ?? '',
  status: item.status,
})

const loadDepartmentList = async (): Promise<void> => {
  if (!permissions.value.list) {
    return
  }

  const requestId = ++listRequestId
  listLoading.value = true
  listError.value = ''
  try {
    const items = await fetchDepartmentList(filters)
    if (requestId !== listRequestId) {
      return
    }

    departments.value = items
    if (!hasActiveFilters()) {
      allDepartments.value = items
      departmentOptionsLoaded.value = true
    }
  } catch {
    if (requestId === listRequestId) {
      departments.value = []
      listError.value = t('department.loadFailed')
    }
  } finally {
    if (requestId === listRequestId) {
      listLoading.value = false
    }
  }
}

const loadAllDepartments = async (force: boolean = false): Promise<void> => {
  if (!permissions.value.list || (departmentOptionsLoaded.value && !force)) {
    return
  }

  allDepartments.value = await fetchDepartmentList()
  departmentOptionsLoaded.value = true
}

const refreshAfterMutation = async (): Promise<void> => {
  if (!hasActiveFilters()) {
    await loadDepartmentList()
    return
  }

  await Promise.allSettled([loadDepartmentList(), loadAllDepartments(true)])
}

const handleSearch = (nextFilters: DepartmentListFilters): void => {
  Object.assign(filters, nextFilters)
  void loadDepartmentList()
}

const handleReset = (nextFilters: DepartmentListFilters): void => {
  Object.assign(filters, nextFilters)
  void loadDepartmentList()
}

const refreshList = (): void => {
  if (!permissions.value.list) {
    return
  }
  void loadDepartmentList()
}

const openCreate = async (parentId: number = 0): Promise<void> => {
  if (!permissions.value.create) {
    return
  }

  formMode.value = 'create'
  editingId.value = null
  replaceFormModel({ ...createInitialFormModel(), parent_id: parentId })
  formVisible.value = true
  formLoading.value = true
  try {
    await loadAllDepartments()
  } finally {
    formLoading.value = false
  }
}

const openDetail = async (item: DepartmentListItem): Promise<void> => {
  if (!permissions.value.query) {
    return
  }

  detailVisible.value = true
  detailLoading.value = true
  detailItem.value = null
  detailParentName.value =
    item.parent_id === null
      ? t('department.form.root')
      : (departmentNames.value[item.parent_id] ?? String(item.parent_id))
  try {
    detailItem.value = await fetchDepartmentDetail(item.dept_id)
  } finally {
    detailLoading.value = false
  }
}

const openEdit = async (item: DepartmentListItem): Promise<void> => {
  if (!permissions.value.edit) {
    return
  }

  formMode.value = 'edit'
  editingId.value = item.dept_id
  replaceFormModel(createFormModelFromDepartment(item))
  formVisible.value = true
  formLoading.value = true
  try {
    await loadAllDepartments()
  } finally {
    formLoading.value = false
  }
}

const saveDepartment = async (model: DepartmentFormModel): Promise<void> => {
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
      await createDepartment(createDepartmentPayload(model))
      message.success(t('department.form.createSuccess'))
    } else if (editingId.value !== null) {
      await updateDepartment(editingId.value, createDepartmentUpdatePayload(model))
      message.success(t('department.form.updateSuccess'))
    } else {
      return
    }

    formVisible.value = false
    await refreshAfterMutation()
  } finally {
    formLoading.value = false
  }
}

const confirmDelete = (item: DepartmentListItem): void => {
  if (!permissions.value.remove) {
    return
  }

  dialog.warning({
    title: t('department.action.confirmDelete'),
    content: t('department.action.confirmDeleteContent'),
    positiveText: t('department.action.delete'),
    negativeText: t('department.form.cancel'),
    onPositiveClick: async () => {
      if (!permissions.value.remove) {
        return
      }

      await deleteDepartment(item.dept_id)
      message.success(t('department.form.deleteSuccess'))
      await refreshAfterMutation()
    },
  })
}

const resetForm = (): void => {
  replaceFormModel(createInitialFormModel())
  editingId.value = null
  formMode.value = 'create'
}

onMounted(() => {
  void loadDepartmentList()
})
</script>

<template>
  <main class="department-page">
    <section class="department-list-panel" aria-labelledby="department-list-title">
      <DepartmentPageHeader
        :title="t('department.title')"
        :description="t('department.description')"
        :total="totalLabel"
        :refresh-loading="listLoading"
        :permissions="permissions"
        @create="openCreate()"
        @refresh="refreshList"
      />

      <DepartmentSearchPanel
        :model="filters"
        :initial-values="initialFilters"
        :loading="listLoading"
        @search="handleSearch"
        @reset="handleReset"
      />

      <div v-if="listError" class="department-page-error">
        <NAlert type="error" :show-icon="false">{{ listError }}</NAlert>
        <NButton
          v-if="permissions.list"
          v-permission="'system:dept:list'"
          size="small"
          @click="refreshList"
        >
          {{ t('department.retry') }}
        </NButton>
      </div>

      <DepartmentTable
        :data="departments"
        :loading="listLoading"
        :permissions="permissions"
        @detail="openDetail"
        @create-child="openCreate($event.dept_id)"
        @edit="openEdit"
        @delete="confirmDelete"
      />
    </section>

    <DepartmentDetailModal
      v-model:show="detailVisible"
      :loading="detailLoading"
      :item="detailItem"
      :parent-name="detailParentName"
    />
    <DepartmentFormModal
      v-model:show="formVisible"
      :mode="formMode"
      :model="formModel"
      :loading="formLoading"
      :departments="allDepartments"
      :editing-id="editingId"
      @submit="saveDepartment"
      @reset="resetForm"
    />
  </main>
</template>

<style lang="scss" scoped>
.department-page {
  display: grid;
  min-width: 0;
  gap: 16px;
  color: var(--app-color-text);
}

.department-list-panel {
  min-width: 0;
  padding: 20px 24px 0;
  overflow: hidden;
  border: 1px solid var(--app-color-border);
  border-radius: 8px;
  background: var(--app-color-surface);
}

.department-list-panel :deep(.app-search-form) {
  margin-bottom: 16px;
}

.department-list-panel :deep(.n-data-table) {
  margin: 16px 0;
}

.department-page-error {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 16px 0;
}

.department-page-error .n-alert {
  flex: 1;
}

@media (width <= 640px) {
  .department-list-panel {
    padding-right: 16px;
    padding-left: 16px;
  }

  .department-list-panel :deep(.n-data-table) {
    margin: 16px -16px 0;
  }
}
</style>
