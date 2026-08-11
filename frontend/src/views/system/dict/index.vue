<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { NAlert, NButton, NPagination, useDialog, useMessage } from 'naive-ui'

import {
  createDictType,
  deleteDictType,
  fetchDictTypeDetail,
  fetchDictTypeList,
  updateDictType,
} from '@/api'
import { useLocale, usePagination } from '@/hooks'
import { useDictionaryStore } from '@/stores'
import type {
  DictTypeCreatePayload,
  DictTypeDetail,
  DictTypeFormModel,
  DictTypeListFilters,
  DictTypeListItem,
  DictTypeUpdatePayload,
  DictionaryFormMode,
} from '@/types'

import DictionaryDetailModal from './components/DictionaryDetailModal.vue'
import DictionaryPageHeader from './components/DictionaryPageHeader.vue'
import DictTypeFormModal from './components/DictTypeFormModal.vue'
import DictTypeSearchPanel from './components/DictTypeSearchPanel.vue'
import DictTypeTable from './components/DictTypeTable.vue'
import { useDictionaryFileActions } from './useDictionaryFileActions'

defineOptions({ name: 'SystemDictTypeView' })

const { t } = useLocale()
const dialog = useDialog()
const message = useMessage()
const router = useRouter()
const dictionaryStore = useDictionaryStore()

const createInitialFilters = (): DictTypeListFilters => ({ name: '', status: null })

const filters = reactive<DictTypeListFilters>(createInitialFilters())
const pagination = usePagination((params) => fetchDictTypeList(params, filters), {
  initialPageSize: 20,
  pageSizes: [20, 50, 100],
})
const formModel = reactive<DictTypeFormModel>({
  dict_name: '',
  dict_type: '',
  status: '1',
  remark: '',
})
const formVisible = ref(false)
const formLoading = ref(false)
const formMode = ref<DictionaryFormMode>('create')
const editingTypeId = ref<number | null>(null)
const detailVisible = ref(false)
const detailLoading = ref(false)
const detailItem = ref<DictTypeDetail | null>(null)

const fileActions = useDictionaryFileActions({
  refresh: pagination.refresh,
  invalidateCache: () => dictionaryStore.clear(),
})
const totalLabel = computed(() =>
  t('dict.total').replace('{count}', String(pagination.total.value)),
)
const pageInfo = computed(() =>
  t('message.pageInfo')
    .replace('{page}', String(pagination.page.value))
    .replace('{pageSize}', String(pagination.pageSize.value)),
)

const resetForm = (): void => {
  Object.assign(formModel, {
    dict_name: '',
    dict_type: '',
    status: '1',
    remark: '',
  })
  editingTypeId.value = null
  formMode.value = 'create'
}

const applyFilters = async (nextFilters: DictTypeListFilters): Promise<void> => {
  Object.assign(filters, nextFilters)
  await pagination.reset()
}

const openCreate = (): void => {
  resetForm()
  formVisible.value = true
}

const openEdit = async (item: DictTypeListItem): Promise<void> => {
  resetForm()
  formMode.value = 'edit'
  editingTypeId.value = item.dict_id
  Object.assign(formModel, {
    dict_name: item.dict_name,
    dict_type: item.dict_type,
    status: item.status,
    remark: item.remark ?? '',
  })
  formVisible.value = true
  formLoading.value = true
  try {
    const detail = await fetchDictTypeDetail(item.dict_id)
    Object.assign(formModel, {
      dict_name: detail.dict_name,
      dict_type: detail.dict_type,
      status: detail.status,
      remark: detail.remark ?? '',
    })
  } finally {
    formLoading.value = false
  }
}

const openDetail = async (item: DictTypeListItem): Promise<void> => {
  detailVisible.value = true
  detailLoading.value = true
  detailItem.value = null
  try {
    detailItem.value = await fetchDictTypeDetail(item.dict_id)
  } finally {
    detailLoading.value = false
  }
}

const save = async (model: DictTypeFormModel): Promise<void> => {
  if (formLoading.value) {
    return
  }

  formLoading.value = true
  try {
    const payload = {
      dict_name: model.dict_name.trim(),
      dict_type: model.dict_type.trim(),
      status: model.status,
      remark: model.remark.trim() || null,
    }
    if (formMode.value === 'create') {
      await createDictType(payload satisfies DictTypeCreatePayload)
      message.success(t('dict.type.form.createSuccess'))
    } else if (editingTypeId.value !== null) {
      await updateDictType(editingTypeId.value, payload satisfies DictTypeUpdatePayload)
      message.success(t('dict.type.form.updateSuccess'))
    }

    dictionaryStore.clear()
    formVisible.value = false
    await pagination.refresh()
  } finally {
    formLoading.value = false
  }
}

const confirmDelete = (item: DictTypeListItem): void => {
  dialog.warning({
    title: t('dict.action.confirmDeleteType'),
    content: t('dict.action.confirmDeleteTypeContent'),
    positiveText: t('dict.action.delete'),
    negativeText: t('dict.form.cancel'),
    onPositiveClick: async () => {
      await deleteDictType(item.dict_id)
      dictionaryStore.remove(item.dict_type)
      message.success(t('dict.type.form.deleteSuccess'))
      await pagination.refresh()
    },
  })
}

const viewData = async (item: DictTypeListItem): Promise<void> => {
  await router.push({ name: 'system-dict-data', query: { dict_type: item.dict_type } })
}

const handleImport = (file: File): void => {
  void fileActions.handleImport(file)
}
</script>

<template>
  <main class="dict-page">
    <section class="dict-list-panel" aria-labelledby="type-dict-list-title">
      <DictionaryPageHeader
        kind="type"
        :total="totalLabel"
        :refresh-loading="pagination.loading.value"
        :export-loading="fileActions.exportLoading.value"
        :import-loading="fileActions.importLoading.value"
        @create="openCreate"
        @refresh="pagination.refresh"
        @export="fileActions.handleExport"
        @import="handleImport"
      />

      <DictTypeSearchPanel
        :model="filters"
        :initial-values="createInitialFilters()"
        :loading="pagination.loading.value"
        @search="applyFilters"
        @reset="applyFilters"
      />

      <div v-if="pagination.error.value" class="dict-page-error">
        <NAlert type="error" :show-icon="false">{{ t('dict.loadFailed') }}</NAlert>
        <NButton size="small" @click="pagination.refresh">{{ t('dict.retry') }}</NButton>
      </div>

      <DictTypeTable
        :data="pagination.data.value"
        :loading="pagination.loading.value"
        @detail="openDetail"
        @view-data="viewData"
        @edit="openEdit"
        @delete="confirmDelete"
      />

      <footer class="dict-page-footer">
        <NPagination v-bind="pagination.pagination.value" />
        <span>{{ pageInfo }}</span>
      </footer>
    </section>

    <DictionaryDetailModal
      v-model:show="detailVisible"
      :loading="detailLoading"
      kind="type"
      :item="detailItem"
    />
    <DictTypeFormModal
      v-model:show="formVisible"
      :mode="formMode"
      :model="formModel"
      :loading="formLoading"
      @submit="save"
      @reset="resetForm"
    />
  </main>
</template>

<style lang="scss" scoped>
.dict-page {
  display: grid;
  min-width: 0;
  gap: 16px;
  color: var(--app-color-text);
}

.dict-list-panel {
  min-width: 0;
  padding: 20px 24px 0;
  overflow: hidden;
  border: 1px solid var(--app-color-border);
  border-radius: 8px;
  background: var(--app-color-surface);
}

.dict-list-panel :deep(.n-data-table) {
  margin: 16px 0;
}

.dict-page-error {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 16px 0;
}

.dict-page-error .n-alert {
  flex: 1;
}

.dict-page-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  min-height: 64px;
  padding: 12px 0;
  border-top: 1px solid var(--app-color-border);
}

.dict-page-footer span {
  margin: 0;
  color: var(--app-color-text-muted);
  font-size: 13px;
}

@media (width <= 640px) {
  .dict-list-panel {
    padding-right: 16px;
    padding-left: 16px;
  }

  .dict-list-panel :deep(.n-data-table) {
    margin: 16px -16px 0;
  }

  .dict-page-footer {
    align-items: flex-start;
    flex-direction: column-reverse;
  }
}
</style>
