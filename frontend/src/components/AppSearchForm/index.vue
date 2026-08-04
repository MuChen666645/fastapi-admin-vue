<script setup lang="ts" generic="T extends AppFormRecord = AppFormRecord">
import { computed, ref, useSlots } from 'vue'
import { NButton, NIcon } from 'naive-ui'
import {
  ChevronDownOutline,
  ChevronUpOutline,
  RefreshOutline,
  SearchOutline,
} from '@vicons/ionicons5'

import AppForm from '@/components/AppForm/index.vue'
import type {
  AppFormExposed,
  AppFormRecord,
  AppFormValidationPayload,
  AppSearchFormExposed,
  AppSearchFormProps,
} from '@/types'

defineOptions({ name: 'AppSearchForm' })

const props = withDefaults(defineProps<AppSearchFormProps<T>>(), {
  fields: () => [],
  layout: () => ({}),
  loading: false,
  disabled: false,
  collapsed: undefined,
  defaultCollapsed: false,
  collapsedFields: 3,
  showToggle: true,
  showSearch: true,
  showReset: true,
  searchOnEnter: true,
  searchText: '搜索',
  resetText: '重置',
  expandText: '展开',
  collapseText: '收起',
})

const emit = defineEmits<{
  search: [model: T, event?: Event]
  reset: [model: T]
  validate: [payload: AppFormValidationPayload]
  'update:collapsed': [collapsed: boolean]
  toggle: [collapsed: boolean]
}>()

const slots = useSlots()
const formRef = ref<AppFormExposed<T> | null>(null)
const localCollapsed = ref(props.defaultCollapsed)

const isCollapsed = computed(() => props.collapsed ?? localCollapsed.value)
const collapsedFieldCount = computed(() => Math.max(0, Math.floor(props.collapsedFields)))
const canToggle = computed(
  () => props.showToggle && props.fields.length > collapsedFieldCount.value,
)
const visibleFields = computed(() => {
  if (!isCollapsed.value || !canToggle.value) {
    return props.fields
  }

  return props.fields.slice(0, collapsedFieldCount.value)
})
const customFields = computed(() =>
  visibleFields.value.filter((field) => Boolean(slots[`field-${field.key}`])),
)
const layout = computed(() => ({
  labelPlacement: 'left' as const,
  labelWidth: 88,
  columns: '1 s:2 m:3',
  responsive: 'screen' as const,
  xGap: 20,
  yGap: 4,
  ...props.layout,
}))
const actionAlignClass = computed(
  () => `app-search-form__actions--${layout.value.actionAlign ?? 'end'}`,
)

const toggle = (): boolean => {
  if (!canToggle.value) {
    return isCollapsed.value
  }

  const nextCollapsed = !isCollapsed.value
  localCollapsed.value = nextCollapsed
  emit('update:collapsed', nextCollapsed)
  emit('toggle', nextCollapsed)
  return nextCollapsed
}

const search = async (event?: Event): Promise<boolean> => formRef.value?.submit(event) ?? false

const reset = (): void => {
  formRef.value?.reset()
}

const handleSearch = (model: T, event?: Event): void => {
  if (props.searchOnEnter === false && event) {
    return
  }

  emit('search', model, event)
}

const handleReset = (model: T): void => {
  emit('reset', model)
}

const handleValidate = (payload: AppFormValidationPayload): void => {
  emit('validate', payload)
}

const getCollapsed = (): boolean => isCollapsed.value

defineExpose<AppSearchFormExposed<T>>({
  search,
  reset,
  toggle,
  isCollapsed: getCollapsed,
  validate: () => formRef.value?.validate() ?? Promise.resolve(false),
  restoreValidation: () => formRef.value?.restoreValidation(),
  getFormInst: () => formRef.value?.getFormInst() ?? null,
  getModel: () => formRef.value?.getModel() ?? props.model,
})
</script>

<template>
  <section class="app-search-form" :class="{ 'app-search-form--collapsed': isCollapsed }">
    <AppForm
      ref="formRef"
      :model="model"
      :initial-values="initialValues"
      :fields="visibleFields"
      :rules="rules"
      :layout="layout"
      :loading="loading"
      :disabled="disabled || loading"
      :show-actions="false"
      @submit="handleSearch"
      @reset="handleReset"
      @validate="handleValidate"
    >
      <template #before="slotProps">
        <slot name="before" v-bind="slotProps" />
      </template>

      <template #content="slotProps">
        <slot name="content" v-bind="slotProps" />
      </template>

      <template #after="slotProps">
        <slot name="after" v-bind="slotProps" />
      </template>

      <template v-for="field in customFields" :key="field.key" #[`field-${field.key}`]="slotProps">
        <slot :name="`field-${field.key}`" v-bind="slotProps" />
      </template>
    </AppForm>

    <div class="app-search-form__actions" :class="actionAlignClass">
      <slot
        name="actions"
        :loading="loading"
        :disabled="disabled || loading"
        :collapsed="isCollapsed"
        :can-toggle="canToggle"
        :search="search"
        :reset="reset"
        :toggle="toggle"
      >
        <NButton
          v-if="showReset"
          attr-type="button"
          :disabled="disabled || loading"
          class="app-search-form__reset"
          @click="reset"
        >
          <template #icon>
            <NIcon><RefreshOutline /></NIcon>
          </template>
          {{ resetText }}
        </NButton>
        <NButton
          v-if="canToggle"
          attr-type="button"
          secondary
          :disabled="disabled || loading"
          class="app-search-form__toggle"
          @click="toggle"
        >
          <template #icon>
            <NIcon>
              <ChevronUpOutline v-if="!isCollapsed" />
              <ChevronDownOutline v-else />
            </NIcon>
          </template>
          {{ isCollapsed ? expandText : collapseText }}
        </NButton>
        <NButton
          v-if="showSearch"
          attr-type="button"
          type="primary"
          :loading="loading"
          :disabled="disabled || loading"
          class="app-search-form__submit"
          @click="search()"
        >
          <template #icon>
            <NIcon><SearchOutline /></NIcon>
          </template>
          {{ searchText }}
        </NButton>
      </slot>
    </div>
  </section>
</template>

<style scoped>
.app-search-form {
  min-width: 0;
}

.app-search-form__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 18px;
}

.app-search-form__actions--start {
  justify-content: flex-start;
}

.app-search-form__actions--center {
  justify-content: center;
}

.app-search-form__actions--end {
  justify-content: flex-end;
}

@media (width <= 640px) {
  .app-search-form__actions,
  .app-search-form__actions--start,
  .app-search-form__actions--center,
  .app-search-form__actions--end {
    justify-content: stretch;
  }

  .app-search-form__actions :deep(.n-button) {
    flex: 1;
  }
}
</style>
