<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import type { LocationQueryValue } from 'vue-router'
import { NAlert, NButton, NPagination, useDialog, useMessage } from 'naive-ui'

import {
  createDictData,
  deleteDictData,
  fetchDictDataDetail,
  fetchDictDataList,
  updateDictData,
} from '@/api'
import { useLocale, usePagination } from '@/hooks'
import { useDictionaryStore } from '@/stores'
import type {
  DictDataCreatePayload,
  DictDataDetail,
  DictDataFormModel,
  DictDataListFilters,
  DictDataListItem,
  DictDataUpdatePayload,
  DictionaryFormMode,
} from '@/types'

import DictDataFormModal from './components/DictDataFormModal.vue'
import DictDataSearchPanel from './components/DictDataSearchPanel.vue'
import DictDataTable from './components/DictDataTable.vue'
import DictionaryDetailModal from './components/DictionaryDetailModal.vue'
import DictionaryPageHeader from './components/DictionaryPageHeader.vue'
import { useDictionaryTypeOptions } from './useDictionaryTypeOptions'

defineOptions({ name: 'SystemDictDataView' })

const { t } = useLocale()
const dialog = useDialog()
const message = useMessage()
const route = useRoute()
const dictionaryStore = useDictionaryStore()

const getDictTypeQuery = (value: LocationQueryValue | LocationQueryValue[] | undefined) =>
  typeof value === 'string' && value.trim() ? value.trim() : null
const createInitialFilters = (): DictDataListFilters => ({
  dict_type: getDictTypeQuery(route.query.dict_type),
  status: null,
})

const filters = reactive<DictDataListFilters>(createInitialFilters())
const pagination = usePagination((params) => fetchDictDataList(params, filters), {
  immediate: false,
  initialPageSize: 20,
  pageSizes: [20, 50, 100],
})
const {
  error: typeOptionsError,
  items: dictTypes,
  load: loadDictTypes,
} = useDictionaryTypeOptions()
const formModel = reactive<DictDataFormModel>({
  dict_sort: 0,
  dict_label: '',
  dict_value: '',
  dict_type: '',
  status: '1',
  remark: '',
})
const formVisible = ref(false)
const formLoading = ref(false)
const formMode = ref<DictionaryFormMode>('create')
const editingDataCode = ref<number | null>(null)
const detailVisible = ref(false)
const detailLoading = ref(false)
const detailItem = ref<DictDataDetail | null>(null)

const hasSelectedDictType = computed(() => Boolean(filters.dict_type))

const refreshData = async (): Promise<void> => {
  if (!hasSelectedDictType.value) {
    return
  }

  await pagination.refresh()
}

const refreshPage = async (): Promise<void> => {
  await Promise.all([refreshData(), loadDictTypes()])
}
const totalLabel = computed(() =>
  t('dict.total').replace('{count}', String(pagination.total.value)),
)
const pageInfo = computed(() =>
  t('message.pageInfo')
    .replace('{page}', String(pagination.page.value))
    .replace('{pageSize}', String(pagination.pageSize.value)),
)

watch(
  () => route.query.dict_type,
  (value) => {
    const dictType = getDictTypeQuery(value)
    filters.dict_type = dictType
    if (dictType) {
      void pagination.reset()
    }
  },
  { immediate: true },
)

const resetForm = (): void => {
  Object.assign(formModel, {
    dict_sort: 0,
    dict_label: '',
    dict_value: '',
    dict_type: filters.dict_type ?? '',
    status: '1',
    remark: '',
  })
  editingDataCode.value = null
  formMode.value = 'create'
}

const applyFilters = async (nextFilters: DictDataListFilters): Promise<void> => {
  if (!nextFilters.dict_type) {
    return
  }

  Object.assign(filters, nextFilters)
  await pagination.reset()
}

const openCreate = (): void => {
  resetForm()
  formVisible.value = true
}

const openEdit = async (item: DictDataListItem): Promise<void> => {
  resetForm()
  formMode.value = 'edit'
  editingDataCode.value = item.dict_code
  Object.assign(formModel, {
    dict_sort: item.dict_sort,
    dict_label: item.dict_label,
    dict_value: item.dict_value,
    dict_type: item.dict_type,
    status: item.status,
    remark: item.remark ?? '',
  })
  formVisible.value = true
  formLoading.value = true
  try {
    const detail = await fetchDictDataDetail(item.dict_code)
    Object.assign(formModel, {
      dict_sort: detail.dict_sort,
      dict_label: detail.dict_label,
      dict_value: detail.dict_value,
      dict_type: detail.dict_type,
      status: detail.status,
      remark: detail.remark ?? '',
    })
  } finally {
    formLoading.value = false
  }
}

const openDetail = async (item: DictDataListItem): Promise<void> => {
  detailVisible.value = true
  detailLoading.value = true
  detailItem.value = null
  try {
    detailItem.value = await fetchDictDataDetail(item.dict_code)
  } finally {
    detailLoading.value = false
  }
}

const save = async (model: DictDataFormModel): Promise<void> => {
  if (formLoading.value) {
    return
  }

  formLoading.value = true
  try {
    const payload = {
      dict_sort: model.dict_sort,
      dict_label: model.dict_label.trim(),
      dict_value: model.dict_value.trim(),
      dict_type: model.dict_type,
      status: model.status,
      remark: model.remark.trim() || null,
    }
    if (formMode.value === 'create') {
      await createDictData(payload satisfies DictDataCreatePayload)
      message.success(t('dict.data.form.createSuccess'))
    } else if (editingDataCode.value !== null) {
      await updateDictData(editingDataCode.value, payload satisfies DictDataUpdatePayload)
      message.success(t('dict.data.form.updateSuccess'))
    }

    dictionaryStore.clear()
    formVisible.value = false
    await refreshData()
  } finally {
    formLoading.value = false
  }
}

const confirmDelete = (item: DictDataListItem): void => {
  dialog.warning({
    title: t('dict.action.confirmDeleteData'),
    content: t('dict.action.confirmDeleteDataContent'),
    positiveText: t('dict.action.delete'),
    negativeText: t('dict.form.cancel'),
    onPositiveClick: async () => {
      await deleteDictData(item.dict_code)
      dictionaryStore.remove(item.dict_type)
      message.success(t('dict.data.form.deleteSuccess'))
      await refreshData()
    },
  })
}
</script>

<template>
  <main class="dict-page">
    <section class="dict-list-panel" aria-labelledby="data-dict-list-title">
      <DictionaryPageHeader
        kind="data"
        :total="totalLabel"
        :refresh-loading="pagination.loading.value"
        @create="openCreate"
        @refresh="refreshPage"
      />

      <DictDataSearchPanel
        :model="filters"
        :initial-values="createInitialFilters()"
        :loading="pagination.loading.value"
        :dict-types="dictTypes"
        @search="applyFilters"
        @reset="applyFilters"
      />

      <div v-if="typeOptionsError" class="dict-page-error">
        <NAlert type="warning" :show-icon="false">{{ t('dict.typeOptionsLoadFailed') }}</NAlert>
        <NButton size="small" @click="loadDictTypes">{{ t('dict.retry') }}</NButton>
      </div>
      <div v-if="!hasSelectedDictType" class="dict-page-empty">
        <NAlert type="info" :show-icon="false">{{ t('dict.data.search.typeRequired') }}</NAlert>
      </div>
      <template v-else>
        <div v-if="pagination.error.value" class="dict-page-error">
          <NAlert type="error" :show-icon="false">{{ t('dict.loadFailed') }}</NAlert>
          <NButton size="small" @click="refreshData">{{ t('dict.retry') }}</NButton>
        </div>

        <DictDataTable
          :data="pagination.data.value"
          :loading="pagination.loading.value"
          @detail="openDetail"
          @edit="openEdit"
          @delete="confirmDelete"
        />

        <footer class="dict-page-footer">
          <NPagination v-bind="pagination.pagination.value" />
          <span>{{ pageInfo }}</span>
        </footer>
      </template>
    </section>

    <DictionaryDetailModal
      v-model:show="detailVisible"
      :loading="detailLoading"
      kind="data"
      :item="detailItem"
    />
    <DictDataFormModal
      v-model:show="formVisible"
      :mode="formMode"
      :model="formModel"
      :loading="formLoading"
      :dict-types="dictTypes"
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

.dict-page-empty {
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
