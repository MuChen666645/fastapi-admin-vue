<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { AddOutline, RefreshOutline } from '@vicons/ionicons5'
import { NAlert, NButton, NIcon, useDialog, useMessage } from 'naive-ui'

import { createMenu, deleteMenu, fetchMenuDetail, fetchMenuList, updateMenu } from '@/api'
import { useLocale } from '@/hooks'
import type {
  MenuCreatePayload,
  MenuDetail,
  MenuFormMode,
  MenuFormModel,
  MenuItem,
  MenuListFilters,
  MenuUpdatePayload,
} from '@/types'

import MenuDetailModal from './components/MenuDetailModal.vue'
import MenuFormModal from './components/MenuFormModal.vue'
import MenuSearchPanel from './components/MenuSearchPanel.vue'
import MenuTable from './components/MenuTable.vue'

defineOptions({ name: 'SystemMenuView' })

const createInitialFilters = (): MenuListFilters => ({ menu_name: '', status: null })

const createInitialFormModel = (): MenuFormModel => ({
  menu_name: '',
  parent_id: 0,
  menu_type: 'C',
  menu_path: '',
  perms: '',
  sort: null,
  icon: '',
  component: '',
  link_url: '',
  is_cache: '0',
  is_hidden: '0',
  status: '1',
  remark: '',
})

const { t } = useLocale()
const message = useMessage()
const dialog = useDialog()
const filters = reactive<MenuListFilters>(createInitialFilters())
const initialFilters = createInitialFilters()
const formModel = reactive<MenuFormModel>(createInitialFormModel())
const menuList = ref<MenuItem[]>([])
const menuOptions = ref<MenuItem[]>([])
const listLoading = ref(false)
const listError = ref<string | null>(null)
const formLoading = ref(false)
const formMode = ref<MenuFormMode>('create')
const formVisible = ref(false)
const editingId = ref<number | null>(null)
const detailItem = ref<MenuDetail | null>(null)
const detailLoading = ref(false)
const detailVisible = ref(false)

const countMenuItems = (items: MenuItem[]): number =>
  items.reduce((total, item) => total + 1 + countMenuItems(item.children), 0)

const totalLabel = computed(() =>
  t('menuManagement.total').replace('{count}', String(countMenuItems(menuList.value))),
)

const replaceFormModel = (model: MenuFormModel): void => {
  Object.assign(formModel, model)
}

const createFormModelFromMenu = (
  item: Pick<MenuItem, keyof MenuItem> | MenuDetail,
): MenuFormModel => ({
  ...createInitialFormModel(),
  menu_name: item.menu_name,
  parent_id: item.parent_id ?? 0,
  menu_type: item.menu_type,
  menu_path: item.menu_path ?? '',
  perms: item.perms ?? '',
  sort: item.sort,
  icon: item.icon ?? '',
  component: item.component ?? '',
  link_url: item.link_url ?? '',
  is_cache: item.is_cache ?? '0',
  is_hidden: item.is_hidden ?? '0',
  status: item.status,
  remark: item.remark ?? '',
})

const toNullableText = (value: string): string | null => value.trim() || null

const createPayload = (model: MenuFormModel): MenuCreatePayload => {
  const base = {
    menu_name: model.menu_name.trim(),
    parent_id: model.parent_id,
    sort: model.sort,
  }

  switch (model.menu_type) {
    case 'F':
      return {
        ...base,
        menu_type: 'F',
        perms: model.perms.trim(),
        remark: model.remark.trim(),
      }
    case 'L':
      return {
        ...base,
        menu_type: 'L',
        menu_path: model.menu_path.trim(),
        icon: toNullableText(model.icon),
        remark: toNullableText(model.remark),
      }
    case 'I':
      return {
        ...base,
        menu_type: 'I',
        menu_path: model.menu_path.trim(),
        component: model.component.trim(),
        link_url: toNullableText(model.link_url),
        icon: toNullableText(model.icon),
        is_cache: model.is_cache,
        is_hidden: model.is_hidden,
        remark: toNullableText(model.remark),
      }
    case 'C':
      return {
        ...base,
        menu_type: 'C',
        menu_path: model.menu_path.trim(),
        icon: toNullableText(model.icon),
        component: toNullableText(model.component),
        is_cache: model.is_cache,
        is_hidden: model.is_hidden,
        remark: toNullableText(model.remark),
      }
  }
}

const updatePayload = (model: MenuFormModel): MenuUpdatePayload => {
  const hasPath = model.menu_type !== 'F'
  const hasComponent = model.menu_type === 'C' || model.menu_type === 'I'
  const hasIcon = model.menu_type !== 'F'
  const hasFlags = hasComponent
  const isButton = model.menu_type === 'F'
  const isIframe = model.menu_type === 'I'

  return {
    menu_name: model.menu_name.trim(),
    parent_id: model.parent_id,
    menu_type: model.menu_type,
    menu_path: hasPath ? toNullableText(model.menu_path) : null,
    component: hasComponent ? toNullableText(model.component) : null,
    icon: hasIcon ? toNullableText(model.icon) : null,
    link_url: isIframe ? toNullableText(model.link_url) : null,
    perms: isButton ? toNullableText(model.perms) : null,
    is_cache: hasFlags ? model.is_cache : '0',
    is_hidden: hasFlags ? model.is_hidden : '0',
    sort: model.sort,
    status: model.status,
    remark: toNullableText(model.remark),
  }
}

const loadMenuList = async (): Promise<void> => {
  listLoading.value = true
  listError.value = null
  try {
    const hasFilters = filters.menu_name.trim() !== '' || filters.status !== null
    const listPromise = fetchMenuList(filters)
    const optionsPromise = hasFilters ? fetchMenuList() : listPromise
    const [items, options] = await Promise.all([listPromise, optionsPromise])
    menuList.value = items
    menuOptions.value = options
  } catch (error: unknown) {
    listError.value = error instanceof Error ? error.message : t('menuManagement.loadFailed')
  } finally {
    listLoading.value = false
  }
}

const handleSearch = async (nextFilters: MenuListFilters): Promise<void> => {
  Object.assign(filters, nextFilters)
  await loadMenuList()
}

const handleReset = async (nextFilters: MenuListFilters): Promise<void> => {
  Object.assign(filters, nextFilters)
  await loadMenuList()
}

const openCreate = (parentId: number = 0): void => {
  formMode.value = 'create'
  editingId.value = null
  replaceFormModel({ ...createInitialFormModel(), parent_id: parentId })
  formVisible.value = true
}

const openEdit = async (item: MenuItem): Promise<void> => {
  formMode.value = 'edit'
  editingId.value = item.menu_id
  replaceFormModel(createFormModelFromMenu(item))
  formVisible.value = true
  formLoading.value = true
  try {
    const detail = await fetchMenuDetail(item.menu_id)
    replaceFormModel(createFormModelFromMenu(detail))
  } finally {
    formLoading.value = false
  }
}

const openDetail = async (item: MenuItem): Promise<void> => {
  detailVisible.value = true
  detailLoading.value = true
  detailItem.value = null
  try {
    detailItem.value = await fetchMenuDetail(item.menu_id)
  } finally {
    detailLoading.value = false
  }
}

const saveMenu = async (model: MenuFormModel): Promise<void> => {
  if (formLoading.value) {
    return
  }

  formLoading.value = true
  try {
    if (formMode.value === 'create') {
      await createMenu(createPayload(model))
      message.success(t('menuManagement.form.createSuccess'))
    } else if (editingId.value !== null) {
      await updateMenu(editingId.value, updatePayload(model))
      message.success(t('menuManagement.form.updateSuccess'))
    }

    formVisible.value = false
    await loadMenuList()
  } finally {
    formLoading.value = false
  }
}

const confirmDelete = (item: MenuItem): void => {
  dialog.warning({
    title: t('menuManagement.action.confirmDelete'),
    content: t('menuManagement.action.confirmDeleteContent'),
    positiveText: t('menuManagement.action.delete'),
    negativeText: t('menuManagement.form.cancel'),
    onPositiveClick: async () => {
      await deleteMenu(item.menu_id)
      message.success(t('menuManagement.form.deleteSuccess'))
      await loadMenuList()
    },
  })
}

const resetForm = (): void => {
  replaceFormModel(createInitialFormModel())
  editingId.value = null
  formMode.value = 'create'
  formLoading.value = false
}

onMounted(() => {
  void loadMenuList()
})
</script>

<template>
  <main class="menu-page">
    <section class="menu-list-panel" aria-labelledby="menu-list-title">
      <header class="menu-list-heading">
        <div>
          <h2 id="menu-list-title">{{ t('menuManagement.title') }}</h2>
          <p>{{ t('menuManagement.description') }}</p>
        </div>
        <div class="menu-page-actions">
          <NButton v-permission="'system:menu:add'" type="primary" @click="openCreate()">
            <template #icon
              ><NIcon><AddOutline /></NIcon
            ></template>
            {{ t('menuManagement.action.create') }}
          </NButton>
          <NButton
            v-permission="'system:menu:list'"
            quaternary
            circle
            :loading="listLoading"
            :aria-label="t('menuManagement.refresh')"
            :title="t('menuManagement.refresh')"
            @click="loadMenuList"
          >
            <template #icon
              ><NIcon><RefreshOutline /></NIcon
            ></template>
          </NButton>
          <span class="menu-total">{{ totalLabel }}</span>
        </div>
      </header>

      <MenuSearchPanel
        :model="filters"
        :initial-values="initialFilters"
        :loading="listLoading"
        @search="handleSearch"
        @reset="handleReset"
      />

      <div v-if="listError" class="menu-page-error">
        <NAlert type="error" :show-icon="false">{{ listError }}</NAlert>
        <NButton v-permission="'system:menu:list'" size="small" @click="loadMenuList">
          {{ t('menuManagement.retry') }}
        </NButton>
      </div>

      <MenuTable
        :data="menuList"
        :loading="listLoading"
        @detail="openDetail"
        @create-child="openCreate($event.menu_id)"
        @edit="openEdit"
        @delete="confirmDelete"
      />
    </section>

    <MenuDetailModal v-model:show="detailVisible" :loading="detailLoading" :item="detailItem" />
    <MenuFormModal
      v-model:show="formVisible"
      :mode="formMode"
      :model="formModel"
      :loading="formLoading"
      :menus="menuOptions"
      :editing-id="editingId"
      @submit="saveMenu"
      @reset="resetForm"
    />
  </main>
</template>

<style lang="scss" scoped>
.menu-page {
  display: grid;
  min-width: 0;
  gap: 16px;
  color: var(--app-color-text);
}

.menu-list-panel {
  min-width: 0;
  padding: 20px 24px 0;
  overflow: hidden;
  border: 1px solid var(--app-color-border);
  border-radius: 8px;
  background: var(--app-color-surface);
}

.menu-list-heading,
.menu-page-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.menu-list-heading {
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 16px;
}

.menu-list-heading h2,
.menu-list-heading p,
.menu-total {
  margin: 0;
}

.menu-list-heading h2 {
  font-size: 16px;
}

.menu-list-heading p {
  margin-top: 6px;
  color: var(--app-color-text-muted);
  font-size: 13px;
  line-height: 1.5;
}

.menu-page-actions {
  justify-content: flex-end;
  gap: 8px;
  flex-wrap: wrap;
}

.menu-total {
  flex: 0 0 auto;
  color: var(--app-color-text-muted);
  font-size: 13px;
}

.menu-list-panel :deep(.app-search-form) {
  margin-bottom: 16px;
}

.menu-list-panel :deep(.n-data-table) {
  margin: 16px 0;
}

.menu-page-error {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 16px 0;
}

.menu-page-error .n-alert {
  flex: 1;
}

@media (width <= 720px) {
  .menu-list-heading {
    align-items: stretch;
    flex-direction: column;
  }

  .menu-page-actions {
    justify-content: flex-start;
  }
}

@media (width <= 640px) {
  .menu-list-panel {
    padding-right: 16px;
    padding-left: 16px;
  }

  .menu-list-panel :deep(.n-data-table) {
    margin: 16px -16px 0;
  }
}
</style>
