<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { NAlert, NButton, NPagination, useDialog, useMessage } from 'naive-ui'

import {
  bindUserRoles,
  createUser,
  deleteUser,
  fetchDepartmentOptions,
  fetchPostOptions,
  fetchRoleOptions,
  fetchUserDetail,
  fetchUserList,
  resetUserPassword,
  updateUser,
} from '@/api'
import { useLocale, usePagination } from '@/hooks'
import type {
  DepartmentOption,
  PostOption,
  RoleOption,
  UserCreatePayload,
  UserDetail,
  UserFormMode,
  UserFormModel,
  UserListFilters,
  UserListItem,
  UserResetPasswordModel,
  UserUpdatePayload,
} from '@/types'
import { isProtectedAdminUser } from '@/utils'
import UserDetailModal from './components/UserDetailModal.vue'
import UserFormModal from './components/UserFormModal.vue'
import UserBatchActions from './components/UserBatchActions.vue'
import UserPageHeader from './components/UserPageHeader.vue'
import UserResetPasswordModal from './components/UserResetPasswordModal.vue'
import UserSearchPanel from './components/UserSearchPanel.vue'
import UserTable from './components/UserTable.vue'
import { useUserBatchActions } from './useUserBatchActions'
import { useUserFileActions } from './useUserFileActions'

defineOptions({ name: 'SystemUserView' })

const createInitialFilters = (): UserListFilters => ({
  username: '',
  nickname: '',
  phone: '',
  email: '',
  create_time: null,
})

const createInitialFormModel = (): UserFormModel => ({
  username: '',
  password: '',
  phone: '',
  email: '',
  nickname: '',
  sex: null,
  status: '1',
  dept_id: null,
  post_ids: [],
  role_ids: [],
  version: null,
})

const createInitialPasswordModel = (): UserResetPasswordModel => ({ password: '' })

const { t } = useLocale()
const dialog = useDialog()
const message = useMessage()

const filters = reactive<UserListFilters>(createInitialFilters())
const initialFilters = createInitialFilters()
const formModel = reactive<UserFormModel>(createInitialFormModel())
const passwordModel = reactive<UserResetPasswordModel>(createInitialPasswordModel())

const departments = ref<DepartmentOption[]>([])
const posts = ref<PostOption[]>([])
const roles = ref<RoleOption[]>([])
const detailItem = ref<UserDetail | null>(null)
const detailLoading = ref(false)
const detailVisible = ref(false)
const formMode = ref<UserFormMode>('create')
const formLoading = ref(false)
const formVisible = ref(false)
const editTarget = ref<UserListItem | null>(null)
const passwordTarget = ref<UserListItem | null>(null)
const passwordLoading = ref(false)
const passwordVisible = ref(false)
const editRolesLoaded = ref(false)
const selectedUserIds = ref<number[]>([])

const pagination = usePagination((params) => fetchUserList(params, filters), {
  initialPageSize: 20,
  immediate: true,
})

const clearSelection = (): void => {
  selectedUserIds.value = []
}

const refreshUserList = async (): Promise<void> => {
  clearSelection()
  await pagination.refresh()
}

const { batchLoading, confirmBatchDelete, handleBatchStatus, handleSelectionChange } =
  useUserBatchActions({
    refresh: refreshUserList,
    selectedUserIds,
  })
const { exportLoading, handleExport, handleImport, importLoading } = useUserFileActions({
  refresh: refreshUserList,
})

const departmentNames = computed<Record<number, string>>(() => {
  const flatten = (items: DepartmentOption[]): DepartmentOption[] =>
    items.flatMap((item) => [item, ...flatten(item.children)])

  return flatten(departments.value).reduce<Record<number, string>>((names, department) => {
    names[department.dept_id] = department.dept_name
    return names
  }, {})
})

const pageInfo = computed(() =>
  t('message.pageInfo')
    .replace('{page}', String(pagination.page.value))
    .replace('{pageSize}', String(pagination.pageSize.value)),
)

const totalLabel = computed(() =>
  t('user.total').replace('{count}', String(pagination.total.value)),
)

const replaceFormModel = (model: UserFormModel): void => {
  Object.assign(formModel, model)
}

const createFormModelFromUser = (item: UserListItem): UserFormModel => ({
  ...createInitialFormModel(),
  username: item.username,
  phone: item.phone ?? '',
  email: item.email ?? '',
  nickname: item.nickname ?? '',
  sex: item.sex,
  status: item.status,
  dept_id: item.dept_id,
  version: item.version,
})

const handleSearch = (nextFilters: UserListFilters): void => {
  Object.assign(filters, nextFilters)
  clearSelection()
  void pagination.reset()
}

const handleReset = (nextFilters: UserListFilters): void => {
  Object.assign(filters, nextFilters)
  clearSelection()
  void pagination.reset()
}

const refreshList = (): void => {
  void refreshUserList()
}

const openCreate = (): void => {
  formMode.value = 'create'
  editTarget.value = null
  editRolesLoaded.value = false
  replaceFormModel(createInitialFormModel())
  formVisible.value = true
}

const openDetail = async (item: UserListItem): Promise<void> => {
  detailVisible.value = true
  detailLoading.value = true
  detailItem.value = null

  try {
    detailItem.value = await fetchUserDetail(item.id)
  } finally {
    detailLoading.value = false
  }
}

const openEdit = async (item: UserListItem): Promise<void> => {
  if (isProtectedAdminUser(item.username)) {
    return
  }

  formMode.value = 'edit'
  editTarget.value = item
  editRolesLoaded.value = false
  replaceFormModel(createFormModelFromUser(item))
  formVisible.value = true
  formLoading.value = true

  try {
    const detail = await fetchUserDetail(item.id)
    replaceFormModel({
      ...createFormModelFromUser(detail.user),
      role_ids: detail.roles.map((role) => role.id),
      post_ids: detail.posts.map((post) => post.post_id),
    })
    editRolesLoaded.value = true
  } finally {
    formLoading.value = false
  }
}

const toNullableText = (value: string): string | null => {
  const trimmed = value.trim()
  return trimmed || null
}

const createPayload = (model: UserFormModel): UserCreatePayload => ({
  username: model.username.trim(),
  password: model.password,
  phone: model.phone.trim(),
  email: toNullableText(model.email),
  nickname: toNullableText(model.nickname),
  sex: model.sex,
  dept_id: model.dept_id,
  post_ids: [...model.post_ids],
  role_ids: [...model.role_ids],
})

const updatePayload = (model: UserFormModel): UserUpdatePayload => {
  const payload: UserUpdatePayload = {
    username: model.username.trim(),
    phone: toNullableText(model.phone),
    email: toNullableText(model.email),
    nickname: toNullableText(model.nickname),
    sex: model.sex,
    status: model.status,
    version: model.version ?? undefined,
  }

  payload.dept_id = model.dept_id
  payload.post_ids = [...model.post_ids]

  return payload
}

const saveUser = async (model: UserFormModel): Promise<void> => {
  if (formLoading.value) {
    return
  }

  formLoading.value = true
  try {
    if (formMode.value === 'create') {
      await createUser(createPayload(model))
      message.success(t('user.form.createSuccess'))
    } else {
      if (!editTarget.value || isProtectedAdminUser(editTarget.value.username)) {
        return
      }

      await updateUser(editTarget.value.id, updatePayload(model))
      if (editRolesLoaded.value) {
        await bindUserRoles(editTarget.value.id, { role_ids: [...model.role_ids] })
      }
      message.success(t('user.form.updateSuccess'))
    }

    formVisible.value = false
    await pagination.refresh()
  } finally {
    formLoading.value = false
  }
}

const openResetPassword = (item: UserListItem): void => {
  if (isProtectedAdminUser(item.username)) {
    return
  }

  passwordTarget.value = item
  Object.assign(passwordModel, createInitialPasswordModel())
  passwordVisible.value = true
}

const savePassword = async (model: UserResetPasswordModel): Promise<void> => {
  if (
    passwordLoading.value ||
    !passwordTarget.value ||
    isProtectedAdminUser(passwordTarget.value.username)
  ) {
    return
  }

  passwordLoading.value = true
  try {
    await resetUserPassword(passwordTarget.value.id, { password: model.password })
    passwordVisible.value = false
    message.success(t('user.form.resetPasswordSuccess'))
  } finally {
    passwordLoading.value = false
  }
}

const confirmDelete = (item: UserListItem): void => {
  if (isProtectedAdminUser(item.username)) {
    return
  }

  dialog.warning({
    title: t('user.action.confirmDelete'),
    content: t('user.action.confirmDeleteContent'),
    positiveText: t('user.action.delete'),
    negativeText: t('user.form.cancel'),
    onPositiveClick: async () => {
      if (isProtectedAdminUser(item.username)) {
        return
      }

      await deleteUser(item.id)
      message.success(t('user.form.deleteSuccess'))
      await pagination.refresh()
    },
  })
}

const loadOptions = async (): Promise<void> => {
  await Promise.allSettled([
    fetchDepartmentOptions().then((items) => {
      departments.value = items
    }),
    fetchPostOptions().then((items) => {
      posts.value = items
    }),
    fetchRoleOptions().then((items) => {
      roles.value = items
    }),
  ])
}

const resetForm = (): void => {
  replaceFormModel(createInitialFormModel())
  editTarget.value = null
  editRolesLoaded.value = false
  formMode.value = 'create'
}

onMounted(() => {
  void loadOptions()
})
</script>

<template>
  <main class="user-page">
    <section class="user-list-panel" aria-labelledby="user-list-title">
      <UserPageHeader
        :title="t('user.title')"
        :description="t('user.description')"
        :total="totalLabel"
        :refresh-loading="pagination.loading.value"
        :export-loading="exportLoading"
        :import-loading="importLoading"
        @create="openCreate"
        @refresh="refreshList"
        @export="handleExport"
        @import="handleImport"
      />

      <UserSearchPanel
        :model="filters"
        :initial-values="initialFilters"
        :loading="pagination.loading.value"
        @search="handleSearch"
        @reset="handleReset"
      />

      <UserBatchActions
        :selected-count="selectedUserIds.length"
        :loading="batchLoading"
        @status="handleBatchStatus"
        @delete="confirmBatchDelete"
      />

      <div v-if="pagination.error.value" class="user-page-error">
        <NAlert type="error" :show-icon="false">{{ t('user.loadFailed') }}</NAlert>
        <NButton v-permission="'system:user:list'" size="small" @click="refreshList">
          {{ t('user.retry') }}
        </NButton>
      </div>

      <UserTable
        :data="pagination.data.value"
        :loading="pagination.loading.value"
        :department-names="departmentNames"
        :selected-row-keys="selectedUserIds"
        @detail="openDetail"
        @edit="openEdit"
        @reset-password="openResetPassword"
        @delete="confirmDelete"
        @update:selected-row-keys="handleSelectionChange"
      />

      <footer class="user-page-footer">
        <NPagination v-bind="pagination.pagination.value" />
        <span>{{ pageInfo }}</span>
      </footer>
    </section>

    <UserDetailModal
      v-model:show="detailVisible"
      :loading="detailLoading"
      :item="detailItem"
      :department-names="departmentNames"
    />
    <UserFormModal
      v-model:show="formVisible"
      :mode="formMode"
      :model="formModel"
      :loading="formLoading"
      :departments="departments"
      :posts="posts"
      :roles="roles"
      @submit="saveUser"
      @reset="resetForm"
    />
    <UserResetPasswordModal
      v-model:show="passwordVisible"
      :model="passwordModel"
      :loading="passwordLoading"
      @submit="savePassword"
      @reset="Object.assign(passwordModel, createInitialPasswordModel())"
    />
  </main>
</template>

<style lang="scss" scoped>
.user-page {
  display: grid;
  min-width: 0;
  gap: 16px;
  color: var(--app-color-text);
}

.user-list-panel {
  min-width: 0;
  padding: 20px 24px 0;
  overflow: hidden;
  border: 1px solid var(--app-color-border);
  border-radius: 8px;
  background: var(--app-color-surface);
}

.user-page-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.user-page-footer span {
  margin: 0;
}

.user-page-footer span {
  flex: 0 0 auto;
  color: var(--app-color-text-muted);
  font-size: 13px;
}

.user-list-panel :deep(.app-search-form) {
  margin-bottom: 16px;
}

.user-list-panel :deep(.n-data-table) {
  margin: 16px 0;
}

.user-page-error {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 16px 0;
}

.user-page-error .n-alert {
  flex: 1;
}

.user-page-footer {
  min-height: 64px;
  padding: 12px 0;
  border-top: 1px solid var(--app-color-border);
}

@media (width <= 640px) {
  .user-list-panel {
    padding-right: 16px;
    padding-left: 16px;
  }

  .user-list-panel :deep(.n-data-table) {
    margin: 16px -16px 0;
  }

  .user-page-footer {
    align-items: flex-start;
    flex-direction: column-reverse;
  }
}
</style>
