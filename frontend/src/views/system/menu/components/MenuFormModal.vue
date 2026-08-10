<script setup lang="ts">
import { computed } from 'vue'
import { CheckmarkDoneOutline } from '@vicons/ionicons5'
import { NButton, NIcon, NModal } from 'naive-ui'
import type { FormItemRule, TreeSelectOption } from 'naive-ui'

import AppForm from '@/components/AppForm/index.vue'
import { useLocale } from '@/hooks'
import type { AppFormField, MenuFormMode, MenuFormModel, MenuItem, MenuType } from '@/types'

defineOptions({ name: 'MenuFormModal' })

interface MenuFormModalProps {
  show: boolean
  mode: MenuFormMode
  model: MenuFormModel
  loading: boolean
  menus: MenuItem[]
  editingId: number | null
}

const props = defineProps<MenuFormModalProps>()
const emit = defineEmits<{
  'update:show': [value: boolean]
  submit: [model: MenuFormModel]
  reset: []
}>()

const { t } = useLocale()

const typeOptions = computed(() => [
  { label: t('menuManagement.type.router'), value: 'C' as const },
  { label: t('menuManagement.type.button'), value: 'F' as const },
  { label: t('menuManagement.type.link'), value: 'L' as const },
  { label: t('menuManagement.type.iframe'), value: 'I' as const },
])

const flagOptions = computed(() => [
  { label: t('menuManagement.flag.no'), value: '0' as const },
  { label: t('menuManagement.flag.yes'), value: '1' as const },
])

const statusOptions = computed(() => [
  { label: t('menuManagement.status.enabled'), value: '1' as const },
  { label: t('menuManagement.status.disabled'), value: '0' as const },
])

const isType = (type: MenuType, ...values: MenuType[]): boolean => values.includes(type)

const toParentTreeOptions = (
  items: MenuItem[],
  currentId: number | null,
  blocked: boolean = false,
): TreeSelectOption[] =>
  items.map((item) => {
    const isCurrent = item.menu_id === currentId
    const isUnavailable = blocked || isCurrent || item.menu_type === 'F'
    const children = toParentTreeOptions(item.children, currentId, blocked || isCurrent)
    return {
      key: item.menu_id,
      label: item.menu_name,
      disabled: isUnavailable,
      ...(children.length > 0 ? { children } : {}),
    }
  })

const parentOptions = computed<TreeSelectOption[]>(() => [
  {
    key: 0,
    label: t('menuManagement.form.root'),
    disabled: props.model.menu_type === 'F',
  },
  ...toParentTreeOptions(props.menus, props.editingId),
])

const requiredTextRule = (message: string, required: boolean): FormItemRule => ({
  required,
  validator: (_rule, value: unknown) =>
    !required || (typeof value === 'string' && value.trim()) ? true : new Error(message),
  trigger: ['input', 'blur', 'change'],
})

const parentRule: FormItemRule = {
  required: true,
  validator: (_rule, value: unknown) => {
    if (typeof value !== 'number' || value < 0) {
      return new Error(t('menuManagement.form.parentPlaceholder'))
    }

    return props.model.menu_type === 'F' && value === 0
      ? new Error(t('menuManagement.form.buttonParentRequired'))
      : true
  },
  trigger: ['change'],
}

const fields = computed<ReadonlyArray<AppFormField<MenuFormModel>>>(() => {
  const type = props.model.menu_type
  const hasPath = isType(type, 'C', 'L', 'I')
  const hasComponent = isType(type, 'C', 'I')
  const hasIcon = isType(type, 'C', 'L', 'I')
  const hasFlags = isType(type, 'C', 'I')
  const isIframe = type === 'I'
  const isButton = type === 'F'

  return [
    {
      key: 'menu_name',
      path: 'menu_name',
      label: t('menuManagement.form.name'),
      required: true,
      requiredMessage: t('menuManagement.form.namePlaceholder'),
      componentProps: {
        clearable: true,
        placeholder: t('menuManagement.form.namePlaceholder'),
      },
    },
    {
      key: 'parent_id',
      path: 'parent_id',
      label: t('menuManagement.form.parent'),
      required: true,
      rules: parentRule,
      type: 'tree-select',
      componentProps: {
        clearable: false,
        defaultExpandAll: true,
        filterable: true,
        options: parentOptions.value,
        placeholder: t('menuManagement.form.parentPlaceholder'),
      },
      valueTransform: (value: unknown) => (typeof value === 'number' ? value : Number(value) || 0),
    },
    {
      key: 'menu_type',
      path: 'menu_type',
      label: t('menuManagement.form.type'),
      required: true,
      type: 'select',
      componentProps: {
        options: typeOptions.value,
        placeholder: t('menuManagement.form.typePlaceholder'),
      },
    },
    {
      key: 'menu_path',
      path: 'menu_path',
      label: t('menuManagement.form.path'),
      hidden: !hasPath,
      required: hasPath,
      requiredMessage: t('menuManagement.form.pathPlaceholder'),
      componentProps: {
        clearable: true,
        placeholder: t('menuManagement.form.pathPlaceholder'),
      },
      span: '1 s:2',
      rules: requiredTextRule(t('menuManagement.form.pathPlaceholder'), hasPath),
    },
    {
      key: 'component',
      path: 'component',
      label: t('menuManagement.form.component'),
      hidden: !hasComponent,
      required: isIframe,
      requiredMessage: t('menuManagement.form.componentPlaceholder'),
      componentProps: {
        clearable: true,
        placeholder: t('menuManagement.form.componentPlaceholder'),
      },
      rules: requiredTextRule(t('menuManagement.form.componentPlaceholder'), isIframe),
    },
    {
      key: 'link_url',
      path: 'link_url',
      label: t('menuManagement.form.linkUrl'),
      hidden: !isIframe,
      componentProps: {
        clearable: true,
        placeholder: t('menuManagement.form.linkUrlPlaceholder'),
      },
    },
    {
      key: 'perms',
      path: 'perms',
      label: t('menuManagement.form.permission'),
      hidden: !isButton,
      required: isButton,
      requiredMessage: t('menuManagement.form.permissionPlaceholder'),
      componentProps: {
        clearable: true,
        placeholder: t('menuManagement.form.permissionPlaceholder'),
      },
      rules: requiredTextRule(t('menuManagement.form.permissionPlaceholder'), isButton),
    },
    {
      key: 'icon',
      path: 'icon',
      label: t('menuManagement.form.icon'),
      hidden: !hasIcon,
      componentProps: {
        clearable: true,
        placeholder: t('menuManagement.form.iconPlaceholder'),
      },
    },
    {
      key: 'sort',
      path: 'sort',
      label: t('menuManagement.form.sort'),
      type: 'number',
      componentProps: {
        clearable: true,
        min: 0,
        placeholder: t('menuManagement.form.sortPlaceholder'),
      },
    },
    {
      key: 'is_cache',
      path: 'is_cache',
      label: t('menuManagement.form.cache'),
      type: 'select',
      hidden: !hasFlags,
      componentProps: {
        options: flagOptions.value,
        placeholder: t('menuManagement.form.flagPlaceholder'),
      },
    },
    {
      key: 'is_hidden',
      path: 'is_hidden',
      label: t('menuManagement.form.hidden'),
      type: 'select',
      hidden: !hasFlags,
      componentProps: {
        options: flagOptions.value,
        placeholder: t('menuManagement.form.flagPlaceholder'),
      },
    },
    {
      key: 'status',
      path: 'status',
      label: t('menuManagement.form.status'),
      type: 'select',
      hidden: () => props.mode !== 'edit',
      componentProps: {
        options: statusOptions.value,
        placeholder: t('menuManagement.form.statusPlaceholder'),
      },
    },
    {
      key: 'remark',
      path: 'remark',
      label: t('menuManagement.form.remark'),
      type: 'textarea',
      required: isButton,
      requiredMessage: t('menuManagement.form.remarkPlaceholder'),
      componentProps: {
        clearable: true,
        placeholder: t('menuManagement.form.remarkPlaceholder'),
        rows: 3,
      },
      rules: requiredTextRule(t('menuManagement.form.remarkPlaceholder'), isButton),
      span: '1 s:2',
    },
  ]
})

const handleShowUpdate = (value: boolean): void => emit('update:show', value)
const handleCancel = (): void => emit('update:show', false)
const handleSubmit = (model: MenuFormModel): void => emit('submit', model)
</script>

<template>
  <NModal
    :show="props.show"
    preset="card"
    class="menu-modal"
    :title="
      props.mode === 'create' ? t('menuManagement.createTitle') : t('menuManagement.editTitle')
    "
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
      <template #actions="{ loading: actionLoading, submit }">
        <NButton attr-type="button" :disabled="actionLoading" @click="handleCancel">
          {{ t('menuManagement.form.cancel') }}
        </NButton>
        <NButton
          v-permission="props.mode === 'create' ? 'system:menu:add' : 'system:menu:edit'"
          attr-type="button"
          type="primary"
          :loading="actionLoading"
          :disabled="actionLoading"
          @click="submit"
        >
          <template #icon>
            <NIcon><CheckmarkDoneOutline /></NIcon>
          </template>
          {{ t('menuManagement.form.save') }}
        </NButton>
      </template>
    </AppForm>
  </NModal>
</template>

<style lang="scss">
.n-card.menu-modal {
  width: min(840px, calc(100vw - 32px));
}
</style>
