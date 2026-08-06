<script setup lang="ts" generic="T extends AppFormRecord = AppFormRecord">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, useSlots, watch } from 'vue'
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
const sectionRef = ref<HTMLElement | null>(null)
const localCollapsed = ref(props.defaultCollapsed)
const measuredCanToggle = ref<boolean | null>(null)
const firstRowFieldCount = ref<number | null>(null)
const isMeasuring = ref(false)
let resizeObserver: ResizeObserver | null = null
let lastMeasuredWidth: number | null = null
let measurementVersion = 0

const isCollapsed = computed(() => props.collapsed ?? localCollapsed.value)
const collapsedFieldCount = computed(() => Math.max(0, Math.floor(props.collapsedFields)))
const countCanToggle = computed(() => props.fields.length > collapsedFieldCount.value)
const visibleCollapsedFieldCount = computed(() =>
  Math.max(collapsedFieldCount.value, firstRowFieldCount.value ?? 0),
)
const canToggle = computed(
  () => props.showToggle && (measuredCanToggle.value ?? countCanToggle.value),
)
const visibleFields = computed(() => {
  if (isMeasuring.value || !isCollapsed.value || !canToggle.value) {
    return props.fields
  }

  return props.fields.slice(0, visibleCollapsedFieldCount.value)
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

const measureFieldLayout = async (width?: number): Promise<void> => {
  const currentVersion = ++measurementVersion
  if (props.fields.length === 0) {
    firstRowFieldCount.value = 0
    measuredCanToggle.value = false
    isMeasuring.value = false
    return
  }

  isMeasuring.value = true
  await nextTick()
  if (currentVersion !== measurementVersion) {
    return
  }

  const section = sectionRef.value
  const fieldElements = Array.from(
    section?.querySelectorAll<HTMLElement>('[data-testid^="app-form-field-"]') ?? [],
  )

  if (fieldElements.length > 0) {
    const rects = fieldElements.map((element) => element.getBoundingClientRect())
    const hasGeometry = rects.some((rect) => rect.width > 0 || rect.height > 0)

    if (!hasGeometry) {
      firstRowFieldCount.value = null
      measuredCanToggle.value = countCanToggle.value
    } else {
      const firstTop = rects[0]?.top ?? 0
      const firstRowCount = rects.filter((rect) => Math.abs(rect.top - firstTop) <= 1).length
      firstRowFieldCount.value = firstRowCount
      measuredCanToggle.value =
        fieldElements.length > Math.max(collapsedFieldCount.value, firstRowCount)
    }
  }

  lastMeasuredWidth = width ?? section?.getBoundingClientRect().width ?? null
  isMeasuring.value = false
}

const handleResize = (entries: ResizeObserverEntry[]): void => {
  const width = entries[0]?.contentRect.width
  if (width === undefined) {
    return
  }

  if (lastMeasuredWidth !== null && Math.abs(width - lastMeasuredWidth) <= 1) {
    return
  }

  void measureFieldLayout(width)
}

watch(
  [
    () => props.fields.length,
    () => props.collapsedFields,
    () => props.layout?.columns,
    () => props.layout?.responsive,
  ],
  () => {
    lastMeasuredWidth = null
    void measureFieldLayout()
  },
)

onMounted(() => {
  void measureFieldLayout()

  if (typeof ResizeObserver === 'undefined' || !sectionRef.value) {
    return
  }

  resizeObserver = new ResizeObserver(handleResize)
  resizeObserver.observe(sectionRef.value)
})

onBeforeUnmount(() => {
  resizeObserver?.disconnect()
  resizeObserver = null
})

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
  <section
    ref="sectionRef"
    class="app-search-form"
    :class="{ 'app-search-form--collapsed': isCollapsed }"
  >
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

<style lang="scss" scoped>
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
