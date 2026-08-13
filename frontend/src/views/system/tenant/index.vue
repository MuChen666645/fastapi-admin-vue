<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { AddOutline, RefreshOutline } from '@vicons/ionicons5'
import { NAlert, NButton, NIcon, useDialog, useMessage } from 'naive-ui'

import {
  addTenantMember,
  createTenant,
  deleteTenant,
  fetchTenantMembers,
  fetchTenants,
  fetchUserOptions,
  removeTenantMember,
  updateTenant,
  updateTenantMember,
} from '@/api'
import { useLocale, usePermission } from '@/hooks'
import type {
  Tenant,
  TenantActionPermissions,
  TenantFilters,
  TenantFormMode,
  TenantFormModel,
  TenantMember,
  TenantMemberAddFormModel,
  TenantStatus,
  UserOption,
} from '@/types'
import { isProtectedAdminUser } from '@/utils'
import TenantDetailModal from './components/TenantDetailModal.vue'
import TenantFormModal from './components/TenantFormModal.vue'
import TenantMemberModal from './components/TenantMemberModal.vue'
import TenantSearchPanel from './components/TenantSearchPanel.vue'
import TenantTable from './components/TenantTable.vue'
import { DEFAULT_TENANT_ID } from './constants'
import {
  createTenantMemberAddPayload,
  createTenantPayload,
  createTenantUpdatePayload,
} from './payloads'

defineOptions({ name: 'SystemTenantView' })

const createInitialFilters = (): TenantFilters => ({ code: '', name: '', status: null })

const createInitialFormModel = (): TenantFormModel => ({
  code: '',
  name: '',
  description: '',
  status: '1',
})

const createInitialMemberAddModel = (): TenantMemberAddFormModel => ({
  user_id: null,
  is_default: false,
})

const { t } = useLocale()
const { hasPermission } = usePermission()
const dialog = useDialog()
const message = useMessage()

const permissions = computed<TenantActionPermissions>(() => ({
  list: hasPermission('system:tenant:list'),
  create: hasPermission('system:tenant:add'),
  edit: hasPermission('system:tenant:edit'),
  remove: hasPermission('system:tenant:remove'),
  memberList: hasPermission('system:tenant:member:list'),
  memberAdd: hasPermission('system:tenant:member:add'),
  memberEdit: hasPermission('system:tenant:member:edit'),
  memberRemove: hasPermission('system:tenant:member:remove'),
}))

const filters = reactive<TenantFilters>(createInitialFilters())
const initialFilters = createInitialFilters()
const formModel = reactive<TenantFormModel>(createInitialFormModel())
const memberAddModel = reactive<TenantMemberAddFormModel>(createInitialMemberAddModel())
const tenants = ref<Tenant[]>([])
const listLoading = ref(false)
const listError = ref<Error | null>(null)
const detailItem = ref<Tenant | null>(null)
const detailVisible = ref(false)
const editTarget = ref<Tenant | null>(null)
const formLoading = ref(false)
const formMode = ref<TenantFormMode>('create')
const formVisible = ref(false)
const memberTenant = ref<Tenant | null>(null)
const memberItems = ref<TenantMember[]>([])
const memberLoading = ref(false)
const memberVisible = ref(false)
const userOptions = ref<UserOption[]>([])
const userOptionsLoading = ref(false)
const canSelectUsers = computed(() => hasPermission('system:user:list'))

const visibleTenants = computed(() => {
  const code = filters.code.trim().toLocaleLowerCase()
  const name = filters.name.trim().toLocaleLowerCase()

  return tenants.value.filter((tenant) => {
    const matchesCode = !code || tenant.code.toLocaleLowerCase().includes(code)
    const matchesName = !name || tenant.name.toLocaleLowerCase().includes(name)
    const matchesStatus = filters.status === null || tenant.status === filters.status
    return matchesCode && matchesName && matchesStatus
  })
})

const totalLabel = computed(() =>
  t('tenant.total').replace('{count}', String(visibleTenants.value.length)),
)

const replaceFormModel = (model: TenantFormModel): void => {
  Object.assign(formModel, model)
}

const replaceMemberAddModel = (model: TenantMemberAddFormModel): void => {
  Object.assign(memberAddModel, model)
}

const createFormModelFromTenant = (item: Tenant): TenantFormModel => ({
  code: item.code,
  name: item.name,
  description: item.description ?? '',
  status: item.status,
})

const isProtectedTenantMember = (item: TenantMember): boolean => isProtectedAdminUser(item.username)

const loadTenants = async (): Promise<void> => {
  if (!permissions.value.list || listLoading.value) {
    return
  }

  listLoading.value = true
  listError.value = null
  try {
    tenants.value = await fetchTenants()
  } catch (error) {
    listError.value = error instanceof Error ? error : new Error(t('tenant.loadFailed'))
  } finally {
    listLoading.value = false
  }
}

const handleSearch = (nextFilters: TenantFilters): void => {
  Object.assign(filters, nextFilters)
}

const handleReset = (nextFilters: TenantFilters): void => {
  Object.assign(filters, nextFilters)
}

const openCreate = (): void => {
  if (!permissions.value.create) {
    return
  }

  formMode.value = 'create'
  editTarget.value = null
  replaceFormModel(createInitialFormModel())
  formVisible.value = true
}

const openDetail = (item: Tenant): void => {
  if (!permissions.value.list) {
    return
  }

  detailItem.value = item
  detailVisible.value = true
}

const openEdit = (item: Tenant): void => {
  if (!permissions.value.edit || item.id === DEFAULT_TENANT_ID) {
    return
  }

  formMode.value = 'edit'
  editTarget.value = item
  replaceFormModel(createFormModelFromTenant(item))
  formVisible.value = true
}

const saveTenant = async (model: TenantFormModel): Promise<void> => {
  if (formLoading.value) {
    return
  }

  const canSave =
    formMode.value === 'create'
      ? permissions.value.create
      : permissions.value.edit && editTarget.value?.id !== DEFAULT_TENANT_ID
  if (!canSave) {
    return
  }

  formLoading.value = true
  try {
    if (formMode.value === 'create') {
      await createTenant(createTenantPayload(model))
      message.success(t('tenant.form.createSuccess'))
    } else if (editTarget.value) {
      await updateTenant(
        editTarget.value.id,
        createTenantUpdatePayload(model, editTarget.value.version),
      )
      message.success(t('tenant.form.updateSuccess'))
    } else {
      return
    }

    formVisible.value = false
    await loadTenants()
  } finally {
    formLoading.value = false
  }
}

const confirmDelete = (item: Tenant): void => {
  if (!permissions.value.remove || item.id === DEFAULT_TENANT_ID) {
    return
  }

  dialog.warning({
    title: t('tenant.action.confirmDelete'),
    content: t('tenant.action.confirmDeleteContent'),
    positiveText: t('tenant.action.delete'),
    negativeText: t('tenant.form.cancel'),
    onPositiveClick: async () => {
      if (!permissions.value.remove || item.id === DEFAULT_TENANT_ID) {
        return
      }

      await deleteTenant(item.id, item.version)
      message.success(t('tenant.form.deleteSuccess'))
      await loadTenants()
    },
  })
}

const loadMembers = async (): Promise<void> => {
  if (!memberTenant.value || !permissions.value.memberList || memberLoading.value) {
    return
  }

  memberLoading.value = true
  try {
    memberItems.value = await fetchTenantMembers(memberTenant.value.id)
  } finally {
    memberLoading.value = false
  }
}

const loadUserOptions = async (): Promise<void> => {
  if (!canSelectUsers.value || userOptionsLoading.value) {
    return
  }

  userOptionsLoading.value = true
  try {
    userOptions.value = await fetchUserOptions()
  } finally {
    userOptionsLoading.value = false
  }
}

const openMembers = async (item: Tenant): Promise<void> => {
  if (!permissions.value.memberList || item.status !== '1') {
    return
  }

  memberTenant.value = item
  memberItems.value = []
  replaceMemberAddModel(createInitialMemberAddModel())
  memberVisible.value = true
  await Promise.all([loadMembers(), loadUserOptions()])
}

const addMember = async (): Promise<void> => {
  if (!memberTenant.value || !permissions.value.memberAdd || memberLoading.value) {
    return
  }

  const payload = createTenantMemberAddPayload(memberAddModel)
  if (!payload) {
    message.error(t('tenant.member.userIdInvalid'))
    return
  }

  memberLoading.value = true
  try {
    await addTenantMember(memberTenant.value.id, payload)
    message.success(t('tenant.member.action.addSuccess'))
    replaceMemberAddModel(createInitialMemberAddModel())
    memberItems.value = await fetchTenantMembers(memberTenant.value.id)
  } finally {
    memberLoading.value = false
  }
}

const updateMember = async (
  item: TenantMember,
  status: TenantStatus,
  isDefault: boolean,
): Promise<void> => {
  if (
    !memberTenant.value ||
    !permissions.value.memberEdit ||
    memberLoading.value ||
    isProtectedTenantMember(item)
  ) {
    return
  }

  memberLoading.value = true
  try {
    await updateTenantMember(memberTenant.value.id, item.user_id, {
      status,
      is_default: isDefault,
      version: item.version,
    })
    message.success(t('tenant.member.action.updateSuccess'))
    memberItems.value = await fetchTenantMembers(memberTenant.value.id)
  } finally {
    memberLoading.value = false
  }
}

const updateMemberStatus = (item: TenantMember, status: TenantStatus): void => {
  void updateMember(item, status, item.is_default && status === '1')
}

const setDefaultMember = (item: TenantMember): void => {
  void updateMember(item, '1', true)
}

const confirmRemoveMember = (item: TenantMember): void => {
  if (!memberTenant.value || !permissions.value.memberRemove || isProtectedTenantMember(item)) {
    return
  }

  dialog.warning({
    title: t('tenant.member.action.confirmRemove'),
    content: t('tenant.member.action.confirmRemoveContent'),
    positiveText: t('tenant.member.action.remove'),
    negativeText: t('tenant.form.cancel'),
    onPositiveClick: async () => {
      if (!memberTenant.value || !permissions.value.memberRemove || isProtectedTenantMember(item)) {
        return
      }

      memberLoading.value = true
      try {
        await removeTenantMember(memberTenant.value.id, item.user_id, item.version)
        message.success(t('tenant.member.action.removeSuccess'))
        memberItems.value = await fetchTenantMembers(memberTenant.value.id)
      } finally {
        memberLoading.value = false
      }
    },
  })
}

const resetForm = (): void => {
  replaceFormModel(createInitialFormModel())
  editTarget.value = null
  formMode.value = 'create'
}

onMounted(() => {
  void loadTenants()
})
</script>

<template>
  <main class="tenant-page">
    <section class="tenant-list-panel" aria-labelledby="tenant-list-title">
      <header class="tenant-list-heading">
        <div>
          <h2 id="tenant-list-title">{{ t('tenant.title') }}</h2>
          <p>{{ t('tenant.description') }}</p>
        </div>
        <div class="tenant-page-actions">
          <NButton
            v-if="permissions.create"
            v-permission="'system:tenant:add'"
            type="primary"
            @click="openCreate"
          >
            <template #icon
              ><NIcon><AddOutline /></NIcon
            ></template>
            {{ t('tenant.action.create') }}
          </NButton>
          <NButton
            v-if="permissions.list"
            v-permission="'system:tenant:list'"
            quaternary
            circle
            :loading="listLoading"
            :aria-label="t('tenant.refresh')"
            :title="t('tenant.refresh')"
            @click="loadTenants"
          >
            <template #icon
              ><NIcon><RefreshOutline /></NIcon
            ></template>
          </NButton>
          <span class="tenant-total">{{ totalLabel }}</span>
        </div>
      </header>

      <TenantSearchPanel
        :model="filters"
        :initial-values="initialFilters"
        :loading="listLoading"
        @search="handleSearch"
        @reset="handleReset"
      />

      <div v-if="listError" class="tenant-page-error">
        <NAlert type="error" :show-icon="false">{{ t('tenant.loadFailed') }}</NAlert>
        <NButton
          v-if="permissions.list"
          v-permission="'system:tenant:list'"
          size="small"
          @click="loadTenants"
        >
          {{ t('tenant.retry') }}
        </NButton>
      </div>

      <TenantTable
        :data="visibleTenants"
        :loading="listLoading"
        :permissions="permissions"
        @detail="openDetail"
        @members="openMembers"
        @edit="openEdit"
        @delete="confirmDelete"
      />
    </section>

    <TenantDetailModal v-model:show="detailVisible" :item="detailItem" />
    <TenantFormModal
      v-model:show="formVisible"
      :mode="formMode"
      :model="formModel"
      :loading="formLoading"
      @submit="saveTenant"
      @reset="resetForm"
    />
    <TenantMemberModal
      v-model:show="memberVisible"
      :tenant="memberTenant"
      :members="memberItems"
      :user-options="userOptions"
      :user-options-loading="userOptionsLoading"
      :can-select-users="canSelectUsers"
      :loading="memberLoading"
      :add-model="memberAddModel"
      :permissions="permissions"
      @update:add-model="replaceMemberAddModel"
      @add="addMember"
      @refresh="loadMembers"
      @status="updateMemberStatus"
      @default="setDefaultMember"
      @remove="confirmRemoveMember"
    />
  </main>
</template>

<style lang="scss" scoped>
.tenant-page {
  display: grid;
  min-width: 0;
  gap: 16px;
  color: var(--app-color-text);
}

.tenant-list-panel {
  min-width: 0;
  padding: 20px 24px;
  overflow: hidden;
  border: 1px solid var(--app-color-border);
  border-radius: 8px;
  background: var(--app-color-surface);
}

.tenant-list-heading,
.tenant-page-actions,
.tenant-page-error {
  display: flex;
  align-items: center;
  gap: 16px;
}

.tenant-list-heading {
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 16px;
}

.tenant-list-heading h2,
.tenant-list-heading p,
.tenant-total {
  margin: 0;
}

.tenant-list-heading h2 {
  font-size: 16px;
}

.tenant-list-heading p {
  margin-top: 6px;
  color: var(--app-color-text-muted);
  font-size: 13px;
  line-height: 1.5;
}

.tenant-page-actions {
  justify-content: flex-end;
  gap: 8px;
  flex-wrap: wrap;
}

.tenant-total {
  flex: 0 0 auto;
  color: var(--app-color-text-muted);
  font-size: 13px;
}

.tenant-page-error {
  margin: 16px 0;
}

.tenant-page-error .n-alert {
  flex: 1;
}

.tenant-list-panel :deep(.app-search-form) {
  margin-bottom: 16px;
}

.tenant-list-panel :deep(.n-data-table) {
  margin-top: 16px;
}

@media (width <= 720px) {
  .tenant-list-heading {
    align-items: stretch;
    flex-direction: column;
  }

  .tenant-page-actions {
    justify-content: flex-start;
  }
}

@media (width <= 640px) {
  .tenant-list-panel {
    padding-right: 16px;
    padding-left: 16px;
  }

  .tenant-list-panel :deep(.n-data-table) {
    margin-right: -16px;
    margin-left: -16px;
  }
}
</style>
