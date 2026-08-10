<script setup lang="ts" generic="T extends AppFormRecord = AppFormRecord">
import { computed, ref } from 'vue'
import {
  NButton,
  NCascader,
  NDatePicker,
  NDivider,
  NEmpty,
  NForm,
  NFormItem,
  NGrid,
  NGridItem,
  NIcon,
  NInput,
  NInputNumber,
  NSelect,
  NSwitch,
  NTreeSelect,
} from 'naive-ui'
import type { Component } from 'vue'
import type { FormInst, FormItemRule, FormValidationError } from 'naive-ui'
import { AddOutline, CheckmarkOutline, RefreshOutline, TrashOutline } from '@vicons/ionicons5'

import type {
  AppFormExposed,
  AppFormField,
  AppFormFieldContext,
  AppFormFieldResolver,
  AppFormGroup,
  AppFormGroupMutation,
  AppFormPath,
  AppFormPathSegment,
  AppFormProps,
  AppFormRecord,
  AppFormValidationPayload,
} from '@/types'

defineOptions({ name: 'AppForm' })

const props = withDefaults(defineProps<AppFormProps<T>>(), {
  fields: () => [],
  groups: () => [],
  layout: () => ({}),
  loading: false,
  disabled: false,
  showActions: true,
  showReset: true,
  submitText: '提交',
  resetText: '重置',
})

const emit = defineEmits<{
  submit: [model: T, event?: Event]
  reset: [model: T]
  validate: [payload: AppFormValidationPayload]
  'group-add': [payload: AppFormGroupMutation]
  'group-remove': [payload: AppFormGroupMutation]
}>()

const formRef = ref<FormInst | null>(null)

const layout = computed(() => ({
  columns: 1,
  responsive: 'self' as const,
  xGap: 20,
  yGap: 4,
  ...props.layout,
}))

const isObjectLike = (value: unknown): value is object =>
  typeof value === 'object' && value !== null

const isRecord = (value: unknown): value is AppFormRecord =>
  isObjectLike(value) && !Array.isArray(value)

const cloneValue = (value: unknown): unknown => {
  if (Array.isArray(value)) {
    return value.map(cloneValue)
  }

  if (isRecord(value)) {
    return Object.fromEntries(Object.entries(value).map(([key, item]) => [key, cloneValue(item)]))
  }

  return value
}

const normalizePath = (path: AppFormPath): AppFormPathSegment[] => {
  if (typeof path !== 'string' && typeof path !== 'number') {
    return [...path]
  }

  return typeof path === 'number' ? [path] : path.split('.').filter(Boolean)
}

const toPathString = (path: AppFormPathSegment[]): string => path.map(String).join('.')

const getPathValue = (source: unknown, path: AppFormPath): unknown => {
  let current = source

  for (const segment of normalizePath(path)) {
    if (!isObjectLike(current)) {
      return undefined
    }

    current = Reflect.get(current, segment)
  }

  return current
}

const setPathValue = (source: unknown, path: AppFormPath, value: unknown): void => {
  const segments = normalizePath(path)
  if (segments.length === 0 || !isObjectLike(source)) {
    return
  }

  let current: unknown = source
  for (const [index, segment] of segments.entries()) {
    if (!isObjectLike(current)) {
      return
    }

    if (index === segments.length - 1) {
      Reflect.set(current, segment, value)
      return
    }

    let next = Reflect.get(current, segment)
    if (!isObjectLike(next)) {
      next = typeof segments[index + 1] === 'number' ? [] : {}
      Reflect.set(current, segment, next)
    }
    current = next
  }
}

const getFieldPath = (
  field: AppFormField<T>,
  group?: AppFormGroup<T>,
  index?: number,
): AppFormPathSegment[] => {
  const fieldPath = normalizePath(field.path)
  if (!group || index === undefined) {
    return fieldPath
  }

  return [...normalizePath(group.path), index, ...fieldPath]
}

const getFieldContext = (
  field: AppFormField<T>,
  group?: AppFormGroup<T>,
  index?: number,
): AppFormFieldContext<T> => {
  const path = getFieldPath(field, group, index)

  return {
    model: props.model,
    field,
    group,
    index,
    path: toPathString(path),
    value: getPathValue(props.model, path),
  }
}

const resolveBoolean = (
  value: AppFormFieldResolver<T> | undefined,
  context: AppFormFieldContext<T>,
): boolean => (typeof value === 'function' ? value(context) : (value ?? false))

const isFieldVisible = (field: AppFormField<T>, group?: AppFormGroup<T>, index?: number): boolean =>
  !resolveBoolean(field.hidden, getFieldContext(field, group, index))

const getFieldSpan = (
  field: AppFormField<T>,
  group?: AppFormGroup<T>,
  index?: number,
): number | string => {
  const context = getFieldContext(field, group, index)
  return typeof field.span === 'function' ? field.span(context) : (field.span ?? 1)
}

const hasRequiredRule = (rules: FormItemRule | FormItemRule[] | undefined): boolean => {
  if (!rules) {
    return false
  }

  return Array.isArray(rules)
    ? rules.some((rule) => rule.required === true)
    : rules.required === true
}

const getFieldRules = (field: AppFormField<T>): FormItemRule | FormItemRule[] | undefined => {
  if (!field.required || hasRequiredRule(field.rules)) {
    return field.rules
  }

  const requiredRule: FormItemRule = {
    required: true,
    message: field.requiredMessage ?? `${field.label ?? '该字段'}不能为空`,
    trigger: ['input', 'blur', 'change'],
  }

  if (!field.rules) {
    return requiredRule
  }

  const customRules = Array.isArray(field.rules) ? field.rules : [field.rules]
  return [requiredRule, ...customRules]
}

const resolveFieldComponent = (field: AppFormField<T>): Component => {
  if (field.component) {
    return field.component
  }

  switch (field.type) {
    case 'password':
      return NInput
    case 'textarea':
      return NInput
    case 'number':
      return NInputNumber
    case 'select':
      return NSelect
    case 'cascader':
      return NCascader
    case 'tree-select':
      return NTreeSelect
    case 'switch':
      return NSwitch
    case 'date':
      return NDatePicker
    case 'input':
    case 'custom':
    default:
      return NInput
  }
}

const getComponentProps = (context: AppFormFieldContext<T>): Record<string, unknown> => {
  const { field } = context
  const resolvedProps =
    typeof field.componentProps === 'function'
      ? field.componentProps(context)
      : (field.componentProps ?? {})
  const disabled = props.disabled || resolveBoolean(field.disabled, context)

  const type =
    field.type === 'password' ? 'password' : field.type === 'textarea' ? 'textarea' : undefined
  return {
    ...resolvedProps,
    ...(type ? { type } : {}),
    ...(disabled ? { disabled: true } : {}),
    class: ['app-form__control', resolvedProps.class],
  }
}

const getFieldModelProps = (context: AppFormFieldContext<T>): Record<string, unknown> => ({
  [context.field.valueProp ?? 'value']: context.value,
})

const getComponentBindings = (context: AppFormFieldContext<T>): Record<string, unknown> => ({
  ...getComponentProps(context),
  ...getFieldModelProps(context),
})

const updateFieldValue = (context: AppFormFieldContext<T>, value: unknown): void => {
  const nextValue = context.field.valueTransform
    ? context.field.valueTransform(value, context)
    : value
  setPathValue(props.model, context.path, nextValue)
}

const getFieldListeners = (
  context: AppFormFieldContext<T>,
): Record<string, (value: unknown) => void> => ({
  [context.field.valueEvent ?? `update:${context.field.valueProp ?? 'value'}`]: (value: unknown) =>
    updateFieldValue(context, value),
})

const getFieldSlotProps = (context: AppFormFieldContext<T>) => ({
  ...context,
  updateValue: (value: unknown) => updateFieldValue(context, value),
  setValue: (value: unknown) => updateFieldValue(context, value),
})

const getGroupItems = (group: AppFormGroup<T>): unknown[] => {
  const value = getPathValue(props.model, group.path)
  return Array.isArray(value) ? value : []
}

const getGroupItemKey = (group: AppFormGroup<T>, value: unknown, index: number): string => {
  if (group.itemKey && isRecord(value)) {
    const itemKey = Reflect.get(value, group.itemKey)
    if (itemKey !== undefined && itemKey !== null) {
      return `${group.key}-${String(itemKey)}`
    }
  }

  return `${group.key}-${index}`
}

const canAddGroup = (group: AppFormGroup<T>): boolean => {
  const maxItems = group.maxItems
  return (
    group.addable !== false && (maxItems === undefined || getGroupItems(group).length < maxItems)
  )
}

const canRemoveGroup = (group: AppFormGroup<T>, index: number): boolean => {
  const minItems = group.minItems ?? 0
  return group.removable !== false && index >= 0 && getGroupItems(group).length > minItems
}

const createGroupItem = (group: AppFormGroup<T>): AppFormRecord => {
  if (group.createItem) {
    return group.createItem()
  }

  if (!group.defaultValue) {
    return {}
  }

  const clonedValue = cloneValue(group.defaultValue)
  return isRecord(clonedValue) ? clonedValue : {}
}

const addGroup = (groupKey: string): boolean => {
  const group = props.groups.find((item) => item.key === groupKey)
  if (!group || !canAddGroup(group)) {
    return false
  }

  const items = getGroupItems(group)
  const value = createGroupItem(group)
  setPathValue(props.model, group.path, [...items, value])
  formRef.value?.restoreValidation()
  emit('group-add', { groupKey, index: items.length, value })
  return true
}

const removeGroup = (groupKey: string, index: number): boolean => {
  const group = props.groups.find((item) => item.key === groupKey)
  const items = group ? getGroupItems(group) : []
  if (!group || index < 0 || index >= items.length || !canRemoveGroup(group, index)) {
    return false
  }

  const [value] = items.slice(index, index + 1)
  setPathValue(
    props.model,
    group.path,
    items.filter((_item, itemIndex) => itemIndex !== index),
  )
  formRef.value?.restoreValidation()
  emit('group-remove', { groupKey, index, value: isRecord(value) ? value : {} })
  return true
}

const isValidationErrorList = (value: unknown): value is FormValidationError => Array.isArray(value)

const validate = async (): Promise<boolean> => {
  if (!formRef.value) {
    return false
  }

  try {
    await formRef.value.validate()
    emit('validate', { valid: true })
    return true
  } catch (error: unknown) {
    const errors = isValidationErrorList(error) ? error : []
    emit('validate', { valid: false, errors })
    return false
  }
}

const submit = async (event?: Event): Promise<boolean> => {
  if (props.loading || !(await validate())) {
    return false
  }

  emit('submit', props.model, event)
  return true
}

const handleSubmit = (event: Event): void => {
  void submit(event)
}

const reset = (): void => {
  if (isRecord(initialSnapshot)) {
    Object.keys(props.model).forEach((key) => {
      if (!Object.prototype.hasOwnProperty.call(initialSnapshot, key)) {
        Reflect.deleteProperty(props.model, key)
      }
    })
    Object.entries(initialSnapshot).forEach(([key, value]) => {
      Reflect.set(props.model, key, cloneValue(value))
    })
  }

  formRef.value?.restoreValidation()
  emit('reset', props.model)
}

const restoreValidation = (): void => {
  formRef.value?.restoreValidation()
}

const getFormInst = (): FormInst | null => formRef.value

const getModel = (): T => props.model

const initialSnapshot = cloneValue(props.initialValues ?? props.model)

defineExpose<AppFormExposed<T>>({
  validate,
  submit,
  reset,
  restoreValidation,
  addGroup,
  removeGroup,
  getFormInst,
  getModel,
})
</script>

<template>
  <NForm
    ref="formRef"
    class="app-form"
    :model="model"
    :rules="rules"
    :disabled="disabled"
    :inline="layout.inline"
    :label-placement="layout.labelPlacement"
    :label-width="layout.labelWidth"
    :label-align="layout.labelAlign"
    :size="layout.size"
    :show-feedback="layout.showFeedback"
    :show-label="layout.showLabel"
    @submit="handleSubmit"
  >
    <slot name="before" :model="model" />

    <NGrid
      v-if="fields.length"
      :cols="layout.columns"
      :responsive="layout.responsive"
      :x-gap="layout.xGap"
      :y-gap="layout.yGap"
      item-responsive
    >
      <template v-for="field in fields" :key="field.key">
        <NGridItem
          v-if="isFieldVisible(field)"
          :span="getFieldSpan(field)"
          :data-testid="`app-form-field-${field.key}`"
        >
          <NFormItem
            :label="field.label"
            :path="getFieldContext(field).path"
            :rule="getFieldRules(field)"
            :required="field.required"
            :show-feedback="field.showFeedback ?? layout.showFeedback"
            :feedback="field.feedback"
          >
            <slot :name="`field-${field.key}`" v-bind="getFieldSlotProps(getFieldContext(field))">
              <component
                :is="resolveFieldComponent(field)"
                v-bind="getComponentBindings(getFieldContext(field))"
                v-on="getFieldListeners(getFieldContext(field))"
              />
            </slot>
          </NFormItem>
        </NGridItem>
      </template>
    </NGrid>

    <slot name="content" :model="model" />
    <slot :model="model" />

    <template v-for="group in groups" :key="group.key">
      <NDivider v-if="group.title || group.description" class="app-form-group__divider" />
      <section class="app-form-group" :data-testid="`app-form-group-${group.key}`">
        <header
          v-if="group.title || group.description || group.addable !== false"
          class="app-form-group__header"
        >
          <div>
            <h3 v-if="group.title" class="app-form-group__title">{{ group.title }}</h3>
            <p v-if="group.description" class="app-form-group__description">
              {{ group.description }}
            </p>
          </div>
          <slot
            :name="`group-${group.key}-actions`"
            :group="group"
            :can-add="canAddGroup(group)"
            :add="() => addGroup(group.key)"
          >
            <NButton
              v-if="canAddGroup(group)"
              size="small"
              secondary
              type="primary"
              attr-type="button"
              :disabled="disabled || loading"
              class="app-form-group__add"
              @click="addGroup(group.key)"
            >
              <template #icon>
                <NIcon><AddOutline /></NIcon>
              </template>
              {{ group.addText ?? '添加' }}
            </NButton>
          </slot>
        </header>

        <NEmpty
          v-if="getGroupItems(group).length === 0 && group.emptyText"
          size="small"
          :description="group.emptyText"
        />

        <div
          v-for="(item, index) in getGroupItems(group)"
          :key="getGroupItemKey(group, item, index)"
          class="app-form-group__item"
          :data-testid="`app-form-group-item-${group.key}-${index}`"
        >
          <div
            v-if="group.title || canRemoveGroup(group, index)"
            class="app-form-group__item-header"
          >
            <span class="app-form-group__item-label"
              >{{ group.title ?? '分组' }} {{ index + 1 }}</span
            >
            <NButton
              v-if="canRemoveGroup(group, index)"
              text
              type="error"
              size="small"
              attr-type="button"
              :disabled="disabled || loading"
              class="app-form-group__remove"
              @click="removeGroup(group.key, index)"
            >
              <template #icon>
                <NIcon><TrashOutline /></NIcon>
              </template>
              {{ group.removeText ?? '删除' }}
            </NButton>
          </div>

          <NGrid
            v-if="group.fields.length"
            :cols="layout.columns"
            :responsive="layout.responsive"
            :x-gap="layout.xGap"
            :y-gap="layout.yGap"
            item-responsive
          >
            <template v-for="field in group.fields" :key="field.key">
              <NGridItem
                v-if="isFieldVisible(field, group, index)"
                :span="getFieldSpan(field, group, index)"
                :data-testid="`app-form-field-${group.key}-${index}-${field.key}`"
              >
                <NFormItem
                  :label="field.label"
                  :path="getFieldContext(field, group, index).path"
                  :rule="getFieldRules(field)"
                  :required="field.required"
                  :show-feedback="field.showFeedback ?? layout.showFeedback"
                  :feedback="field.feedback"
                >
                  <slot
                    :name="`field-${group.key}-${field.key}`"
                    v-bind="getFieldSlotProps(getFieldContext(field, group, index))"
                  >
                    <component
                      :is="resolveFieldComponent(field)"
                      v-bind="getComponentBindings(getFieldContext(field, group, index))"
                      v-on="getFieldListeners(getFieldContext(field, group, index))"
                    />
                  </slot>
                </NFormItem>
              </NGridItem>
            </template>
          </NGrid>
        </div>
      </section>
    </template>

    <slot name="after" :model="model" />

    <div v-if="showActions" class="app-form__actions">
      <slot name="actions" :loading="loading" :disabled="disabled" :submit="submit" :reset="reset">
        <NButton
          v-if="showReset"
          attr-type="button"
          :disabled="disabled || loading"
          class="app-form__reset"
          @click="reset"
        >
          <template #icon>
            <NIcon><RefreshOutline /></NIcon>
          </template>
          {{ resetText }}
        </NButton>
        <NButton
          attr-type="submit"
          type="primary"
          :loading="loading"
          :disabled="disabled"
          class="app-form__submit"
        >
          <template #icon>
            <NIcon><CheckmarkOutline /></NIcon>
          </template>
          {{ submitText }}
        </NButton>
      </slot>
    </div>
  </NForm>
</template>

<style lang="scss" scoped>
.app-form__actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid var(--app-color-border);
}

.app-form__control {
  width: 100%;
}

.app-form-group__divider {
  margin: 24px 0 18px;
}

.app-form-group__header,
.app-form-group__item-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.app-form-group__header {
  margin-bottom: 12px;
}

.app-form-group__title,
.app-form-group__description,
.app-form-group__item-label {
  margin: 0;
}

.app-form-group__title {
  font-size: 15px;
  font-weight: 700;
}

.app-form-group__description {
  margin-top: 4px;
  color: var(--app-color-text-muted);
  font-size: 13px;
}

.app-form-group__item {
  padding: 16px;
  border: 1px solid var(--app-color-border);
  border-radius: 8px;
}

.app-form-group__item + .app-form-group__item {
  margin-top: 12px;
}

.app-form-group__item-header {
  align-items: center;
  margin-bottom: 12px;
}

.app-form-group__item-label {
  color: var(--app-color-text-muted);
  font-size: 13px;
  font-weight: 600;
}

@media (width <= 640px) {
  .app-form__actions {
    justify-content: stretch;
  }

  .app-form__actions :deep(.n-button) {
    flex: 1;
  }
}
</style>
