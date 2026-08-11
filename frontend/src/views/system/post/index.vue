<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { NAlert, NButton, NPagination, useDialog, useMessage } from 'naive-ui'

import { createPost, deletePost, fetchPostDetail, fetchPostList, updatePost } from '@/api'
import { useLocale, usePagination, usePermission } from '@/hooks'
import type {
  PostActionPermissions,
  PostDetail,
  PostFormMode,
  PostFormModel,
  PostListFilters,
  PostListItem,
} from '@/types'
import PostDetailModal from './components/PostDetailModal.vue'
import PostFormModal from './components/PostFormModal.vue'
import PostPageHeader from './components/PostPageHeader.vue'
import PostSearchPanel from './components/PostSearchPanel.vue'
import PostTable from './components/PostTable.vue'
import { createPostPayload, createPostUpdatePayload } from './payloads'

defineOptions({ name: 'SystemPostView' })

const createInitialFilters = (): PostListFilters => ({ name: '', status: null })

const createInitialFormModel = (): PostFormModel => ({
  post_code: '',
  post_name: '',
  post_sort: 0,
  remark: '',
  status: '1',
})

const { t } = useLocale()
const { hasPermission } = usePermission()
const dialog = useDialog()
const message = useMessage()

const permissions = computed<PostActionPermissions>(() => ({
  list: hasPermission('system:post:list'),
  query: hasPermission('system:post:query'),
  create: hasPermission('system:post:add'),
  edit: hasPermission('system:post:edit'),
  remove: hasPermission('system:post:remove'),
}))

const filters = reactive<PostListFilters>(createInitialFilters())
const initialFilters = createInitialFilters()
const formModel = reactive<PostFormModel>(createInitialFormModel())
const detailItem = ref<PostDetail | null>(null)
const detailLoading = ref(false)
const detailVisible = ref(false)
const editingId = ref<number | null>(null)
const formLoading = ref(false)
const formMode = ref<PostFormMode>('create')
const formVisible = ref(false)

const pagination = usePagination((params) => fetchPostList(params, filters), {
  immediate: false,
  initialPageSize: 20,
  pageSizes: [20, 50, 100],
})

const totalLabel = computed(() =>
  t('post.total').replace('{count}', String(pagination.total.value)),
)

const pageInfo = computed(() =>
  t('post.pageInfo')
    .replace('{page}', String(pagination.page.value))
    .replace('{pageSize}', String(pagination.pageSize.value)),
)

const replaceFormModel = (model: PostFormModel): void => {
  Object.assign(formModel, model)
}

const createFormModelFromPost = (item: PostListItem): PostFormModel => ({
  post_code: item.post_code,
  post_name: item.post_name,
  post_sort: item.post_sort,
  remark: item.remark ?? '',
  status: item.status,
})

const refreshPostList = async (): Promise<void> => {
  if (!permissions.value.list) {
    return
  }

  await pagination.refresh()
}

const handleSearch = (nextFilters: PostListFilters): void => {
  if (!permissions.value.list) {
    return
  }

  Object.assign(filters, nextFilters)
  void pagination.reset()
}

const handleReset = (nextFilters: PostListFilters): void => {
  if (!permissions.value.list) {
    return
  }

  Object.assign(filters, nextFilters)
  void pagination.reset()
}

const refreshList = (): void => {
  void refreshPostList()
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

const openDetail = async (item: PostListItem): Promise<void> => {
  if (!permissions.value.query) {
    return
  }

  detailVisible.value = true
  detailLoading.value = true
  detailItem.value = null
  try {
    detailItem.value = await fetchPostDetail(item.post_id)
  } finally {
    detailLoading.value = false
  }
}

const openEdit = (item: PostListItem): void => {
  if (!permissions.value.edit) {
    return
  }

  formMode.value = 'edit'
  editingId.value = item.post_id
  replaceFormModel(createFormModelFromPost(item))
  formVisible.value = true
}

const savePost = async (model: PostFormModel): Promise<void> => {
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
      await createPost(createPostPayload(model))
      message.success(t('post.form.createSuccess'))
    } else if (editingId.value !== null) {
      await updatePost(editingId.value, createPostUpdatePayload(model))
      message.success(t('post.form.updateSuccess'))
    } else {
      return
    }

    formVisible.value = false
    await refreshPostList()
  } finally {
    formLoading.value = false
  }
}

const confirmDelete = (item: PostListItem): void => {
  if (!permissions.value.remove) {
    return
  }

  dialog.warning({
    title: t('post.action.confirmDelete'),
    content: t('post.action.confirmDeleteContent'),
    positiveText: t('post.action.delete'),
    negativeText: t('post.form.cancel'),
    onPositiveClick: async () => {
      if (!permissions.value.remove) {
        return
      }

      await deletePost(item.post_id)
      message.success(t('post.form.deleteSuccess'))
      await refreshPostList()
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
  <main class="post-page">
    <section class="post-list-panel" aria-labelledby="post-list-title">
      <PostPageHeader
        :title="t('post.title')"
        :description="t('post.description')"
        :total="totalLabel"
        :refresh-loading="pagination.loading.value"
        :permissions="permissions"
        @create="openCreate"
        @refresh="refreshList"
      />

      <PostSearchPanel
        :model="filters"
        :initial-values="initialFilters"
        :loading="pagination.loading.value"
        @search="handleSearch"
        @reset="handleReset"
      />

      <div v-if="pagination.error.value" class="post-page-error">
        <NAlert type="error" :show-icon="false">{{ t('post.loadFailed') }}</NAlert>
        <NButton
          v-if="permissions.list"
          v-permission="'system:post:list'"
          size="small"
          @click="refreshList"
        >
          {{ t('post.retry') }}
        </NButton>
      </div>

      <PostTable
        :data="pagination.data.value"
        :loading="pagination.loading.value"
        :permissions="permissions"
        @detail="openDetail"
        @edit="openEdit"
        @delete="confirmDelete"
      />

      <footer v-if="permissions.list" class="post-page-footer">
        <NPagination v-bind="pagination.pagination.value" />
        <span>{{ pageInfo }}</span>
      </footer>
    </section>

    <PostDetailModal v-model:show="detailVisible" :loading="detailLoading" :item="detailItem" />
    <PostFormModal
      v-model:show="formVisible"
      :mode="formMode"
      :model="formModel"
      :loading="formLoading"
      @submit="savePost"
      @reset="resetForm"
    />
  </main>
</template>

<style lang="scss" scoped>
.post-page {
  display: grid;
  min-width: 0;
  gap: 16px;
  color: var(--app-color-text);
}

.post-list-panel {
  min-width: 0;
  padding: 20px 24px 0;
  overflow: hidden;
  border: 1px solid var(--app-color-border);
  border-radius: 8px;
  background: var(--app-color-surface);
}

.post-page-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  min-height: 64px;
  padding: 12px 0;
  border-top: 1px solid var(--app-color-border);
}

.post-page-footer span {
  flex: 0 0 auto;
  color: var(--app-color-text-muted);
  font-size: 13px;
}

.post-list-panel :deep(.app-search-form) {
  margin-bottom: 16px;
}

.post-list-panel :deep(.n-data-table) {
  margin: 16px 0;
}

.post-page-error {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 16px 0;
}

.post-page-error .n-alert {
  flex: 1;
}

@media (width <= 640px) {
  .post-list-panel {
    padding-right: 16px;
    padding-left: 16px;
  }

  .post-list-panel :deep(.n-data-table) {
    margin: 16px -16px 0;
  }

  .post-page-footer {
    align-items: flex-start;
    flex-direction: column-reverse;
  }
}
</style>
