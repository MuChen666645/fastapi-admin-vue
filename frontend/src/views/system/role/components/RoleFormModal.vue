<script setup lang="ts">
import { computed } from 'vue'
import { CheckmarkDoneOutline } from '@vicons/ionicons5'
import { NButton, NDivider, NEmpty, NFormItem, NIcon, NModal, NTag, NTreeSelect } from 'naive-ui'
import type { FormItemRule, TreeSelectOption } from 'naive-ui'

import AppForm from '@/components/AppForm/index.vue'
import { useLocale } from '@/hooks'
import type { AppFormField, DepartmentOption, MenuItem, RoleFormMode, RoleFormModel } from '@/types'

defineOptions({ name: 'RoleFormModal' })

interface RoleFormModalProps {
  show: boolean
  mode: RoleFormMode
  model: RoleFormModel
  loading: boolean
  menus: MenuItem[]
  departments: DepartmentOption[]
}

const props = defineProps<RoleFormModalProps>()
const emit = defineEmits<{
  'update:show': [value: boolean]
  'update:model': [value: Partial<RoleFormModel>]
  submit: [model: RoleFormModel]
  reset: []
}>()

const { t } = useLocale()

const dataScopeOptions = computed(() => [
  { label: t('role.dataScope.all'), value: '1' as const },
  { label: t('role.dataScope.custom'), value: '2' as const },
  { label: t('role.dataScope.current'), value: '3' as const },
  { label: t('role.dataScope.currentAndBelow'), value: '4' as const },
  { label: t('role.dataScope.self'), value: '5' as const },
])

const statusOptions = computed(() => [
  { label: t('role.status.enabled'), value: '1' as const },
  { label: t('role.status.disabled'), value: '0' as const },
])

const fields = computed<ReadonlyArray<AppFormField<RoleFormModel>>>(() => [
  {
    key: 'name',
    path: 'name',
    label: t('role.form.name'),
    required: true,
    requiredMessage: t('role.form.namePlaceholder'),
    componentProps: { clearable: true, placeholder: t('role.form.namePlaceholder') },
  },
  {
    key: 'code',
    path: 'code',
    label: t('role.form.code'),
    required: true,
    requiredMessage: t('role.form.codePlaceholder'),
    disabled: () => props.mode === 'edit',
    componentProps: { clearable: true, placeholder: t('role.form.codePlaceholder') },
  },
  {
    key: 'description',
    path: 'description',
    label: t('role.form.description'),
    type: 'textarea',
    componentProps: {
      clearable: true,
      placeholder: t('role.form.descriptionPlaceholder'),
      rows: 3,
    },
    span: '1 s:2',
  },
  {
    key: 'data_scope',
    path: 'data_scope',
    label: t('role.form.dataScope'),
    type: 'select',
    componentProps: {
      options: dataScopeOptions.value,
      placeholder: t('role.form.dataScopePlaceholder'),
    },
  },
  {
    key: 'status',
    path: 'status',
    label: t('role.form.status'),
    type: 'select',
    hidden: () => props.mode !== 'edit',
    componentProps: {
      options: statusOptions.value,
      placeholder: t('role.form.statusPlaceholder'),
    },
  },
])

const toMenuTreeOptions = (items: MenuItem[]): TreeSelectOption[] =>
  items.map((item) => {
    const children = toMenuTreeOptions(item.children)
    return {
      key: item.menu_id,
      label: item.menu_name,
      disabled: item.status !== '1',
      ...(children.length > 0 ? { children } : {}),
    }
  })

const toDepartmentTreeOptions = (items: DepartmentOption[]): TreeSelectOption[] =>
  items.map((item) => {
    const children = toDepartmentTreeOptions(item.children)
    return {
      key: item.dept_id,
      label: item.dept_name,
      disabled: item.status !== '1',
      ...(children.length > 0 ? { children } : {}),
    }
  })

const menuTreeOptions = computed(() => toMenuTreeOptions(props.menus))
const departmentTreeOptions = computed(() => toDepartmentTreeOptions(props.departments))
const departmentRules = computed<FormItemRule>(() => ({
  required: props.model.data_scope === '2',
  validator: (_rule, value: unknown) => {
    if (props.model.data_scope !== '2') {
      return true
    }

    return Array.isArray(value) && value.length > 0
      ? true
      : new Error(t('role.form.customDepartmentRequired'))
  },
  trigger: ['change'],
}))

const toNumberKeys = (keys: Array<string | number> | null): number[] =>
  keys?.filter((key): key is number => typeof key === 'number') ?? []

const handleMenuKeys = (keys: Array<string | number> | null): void => {
  emit('update:model', { menu_ids: toNumberKeys(keys) })
}

const handleDepartmentKeys = (keys: Array<string | number> | null): void => {
  emit('update:model', { dept_ids: toNumberKeys(keys) })
}

const handleShowUpdate = (value: boolean): void => emit('update:show', value)
const handleCancel = (): void => emit('update:show', false)
const handleSubmit = (model: RoleFormModel): void => emit('submit', model)
</script>

<template>
  <NModal
    :show="props.show"
    preset="card"
    class="role-modal"
    :title="props.mode === 'create' ? t('role.createTitle') : t('role.editTitle')"
    :mask-closable="false"
    @update:show="handleShowUpdate"
    @after-leave="emit('reset')"
  >
    <AppForm
      :model="props.model"
      :fields="fields"
      :loading="props.loading"
      :show-reset="false"
      :layout="{
        labelPlacement: 'top',
        columns: '1 s:2',
        responsive: 'screen',
        xGap: 16,
        yGap: 4,
      }"
      @submit="handleSubmit"
    >
      <template #after>
        <NDivider />
        <section class="role-permission-section">
          <div class="role-section-heading">
            <div>
              <h3>{{ t('role.form.menu') }}</h3>
              <p>{{ t('role.form.menuDescription') }}</p>
            </div>
          </div>
          <NFormItem>
            <NTreeSelect
              v-if="menuTreeOptions.length > 0"
              cascade
              checkable
              clearable
              default-expand-all
              :disabled="props.loading"
              filterable
              multiple
              :options="menuTreeOptions"
              :placeholder="t('role.form.menu')"
              show-path
              class="role-tree-select"
              :value="props.model.menu_ids"
              @update:value="handleMenuKeys"
            />
            <NEmpty v-else size="small" :description="t('role.form.noOptions')" />
          </NFormItem>
        </section>

        <section class="role-permission-section">
          <div class="role-section-heading">
            <div>
              <h3>{{ t('role.form.department') }}</h3>
              <p>{{ t('role.form.departmentDescription') }}</p>
            </div>
          </div>
          <NFormItem path="dept_ids" :rule="departmentRules">
            <NTreeSelect
              v-if="props.model.data_scope === '2' && departmentTreeOptions.length > 0"
              checkable
              clearable
              default-expand-all
              :disabled="props.loading"
              filterable
              multiple
              :options="departmentTreeOptions"
              :placeholder="t('role.form.department')"
              show-path
              class="role-tree-select"
              :value="props.model.dept_ids"
              @update:value="handleDepartmentKeys"
            />
            <NEmpty v-else size="small" :description="t('role.form.noOptions')" />
          </NFormItem>
        </section>

        <section
          v-if="props.model.field_permission_codes.length > 0"
          class="role-permission-section"
        >
          <div class="role-section-heading">
            <div>
              <h3>{{ t('role.form.fieldPermissions') }}</h3>
            </div>
          </div>
          <div class="role-field-permissions">
            <NTag v-for="code in props.model.field_permission_codes" :key="code" size="small">
              {{ code }}
            </NTag>
          </div>
        </section>
      </template>
      <template #actions="{ loading: actionLoading, submit }">
        <NButton attr-type="button" :disabled="actionLoading" @click="handleCancel">
          {{ t('role.form.cancel') }}
        </NButton>
        <NButton
          v-permission="props.mode === 'create' ? 'system:role:add' : 'system:role:edit'"
          attr-type="button"
          type="primary"
          :loading="actionLoading"
          :disabled="actionLoading"
          @click="submit"
        >
          <template #icon
            ><NIcon><CheckmarkDoneOutline /></NIcon
          ></template>
          {{ t('role.form.save') }}
        </NButton>
      </template>
    </AppForm>
  </NModal>
</template>

<style lang="scss">
.n-card.role-modal {
  width: min(820px, calc(100vw - 32px));
}

.role-permission-section {
  padding: 8px 0 16px;
}

.role-section-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.role-section-heading h3,
.role-section-heading p {
  margin: 0;
}

.role-section-heading h3 {
  font-size: 14px;
}

.role-section-heading p {
  margin-top: 4px;
  color: var(--app-color-text-muted);
  font-size: 12px;
}

.role-permission-section .n-form-item {
  margin-top: 12px;
}

.role-tree-select {
  width: 100%;
}

.role-tree-select .n-base-selection {
  min-height: 40px;
}

.role-field-permissions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}
</style>
