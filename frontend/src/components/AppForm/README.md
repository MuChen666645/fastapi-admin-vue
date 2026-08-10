# AppForm 使用文档

`AppForm` 是基于 Naive UI `NForm` 的通用提交表单组件，负责字段渲染、布局、标准校验、动态分组和提交前拦截。它不负责调用 API，页面通过 `@submit` 接收校验后的 model 并完成业务提交。

## 基础用法

```vue
<script setup lang="ts">
import { reactive, ref } from 'vue'

import AppForm from '@/components/AppForm/index.vue'
import type { AppFormField } from '@/types'

interface UserForm {
  username: string
  email: string
}

const form = reactive<UserForm>({ username: '', email: '' })
const submitting = ref(false)
const fields: AppFormField[] = [
  { key: 'username', path: 'username', label: '用户名', required: true },
  {
    key: 'email',
    path: 'email',
    label: '邮箱',
    rules: [{ type: 'email', message: '请输入正确的邮箱地址', trigger: ['input', 'blur'] }],
  },
]

const handleSubmit = async (model: UserForm): Promise<void> => {
  submitting.value = true
  try {
    // 在页面或领域 Store 中调用 @/api 下已经核实的真实接口。
    void model
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <AppForm :model="form" :fields="fields" :loading="submitting" @submit="handleSubmit" />
</template>
```

提交事件只会在 `NForm.validate()` 成功后触发。`loading` 为 `true` 时，组件会拒绝重复提交并禁用默认操作按钮。

## 字段配置

| 属性                       | 说明                                                                                                           |
| -------------------------- | -------------------------------------------------------------------------------------------------------------- |
| `key`                      | 字段渲染和插槽使用的唯一标识。                                                                                 |
| `path`                     | model 中的字段路径，支持 `user.name` 或路径数组。                                                              |
| `label`                    | 表单项标签。                                                                                                   |
| `type`                     | `input`、`password`、`textarea`、`number`、`select`、`cascader`、`tree-select`、`switch`、`date` 或 `custom`。 |
| `component`                | 自定义 Vue 组件；默认使用 `value` 和 `update:value`。                                                          |
| `componentProps`           | 控件属性或根据字段上下文生成属性。`select` 的 options 等配置放在这里。                                         |
| `valueTransform`           | 在写回 model 前转换控件值，适合将 `tree-select` 清空后的 `null` 归一化为数组。                                 |
| `valueProp` / `valueEvent` | 自定义组件的值属性和更新事件，例如 `modelValue` / `update:modelValue`。                                        |
| `rules`                    | Naive UI `FormItemRule` 或规则数组。                                                                           |
| `required`                 | 自动生成必填规则；`requiredMessage` 可覆盖提示文案。                                                           |
| `hidden` / `disabled`      | 布尔值或根据字段上下文计算的状态。隐藏字段不会参与当前渲染和校验。                                             |
| `span`                     | 当前字段在栅格布局中的占位列数。                                                                               |

内置控件会根据 `type` 自动选择：

```ts
const fields: AppFormField[] = [
  {
    key: 'departments',
    path: 'departments',
    label: '部门',
    type: 'tree-select',
    componentProps: {
      multiple: true,
      options: [{ key: 1, label: '总部' }],
    },
    valueTransform: (value) => (Array.isArray(value) ? value : []),
  },
  { key: 'title', path: 'title', label: '标题', required: true },
  {
    key: 'priority',
    path: 'priority',
    label: '优先级',
    type: 'select',
    componentProps: {
      options: [
        { label: '普通', value: 'normal' },
        { label: '紧急', value: 'urgent' },
      ],
    },
  },
  { key: 'enabled', path: 'enabled', label: '启用', type: 'switch' },
]
```

## 表单布局

通过 `layout` 统一设置 Naive UI 表单属性和栅格布局：

```vue
<AppForm
  :model="form"
  :fields="fields"
  :layout="{
    labelPlacement: 'top',
    columns: '1 s:2 m:3',
    responsive: 'screen',
    xGap: 20,
    yGap: 8,
  }"
/>
```

支持 `labelPlacement`、`labelWidth`、`labelAlign`、`size`、`inline`、`showFeedback`、`showLabel`、`columns`、`responsive`、`xGap` 和 `yGap`。

## 自定义字段

字段插槽名称为 `field-${field.key}`，插槽参数提供当前值、model、路径和 `setValue`：

```vue
<AppForm :model="form" :fields="fields">
  <template #field-description="{ value, setValue }">
    <NInput
      type="textarea"
      :value="typeof value === 'string' ? value : ''"
      @update:value="setValue"
    />
  </template>
</AppForm>
```

也可以通过 `component` 传入自定义组件；如果组件不使用 `value` / `update:value`，配置 `valueProp` 和 `valueEvent`。

## 动态分组

分组的 `path` 必须指向 model 中的数组。`fields` 使用相对于数组项的路径：

```ts
const form = reactive({
  reviewers: [{ id: 1, name: '', role: 'owner' }],
})

const groups: AppFormGroup[] = [
  {
    key: 'reviewers',
    path: 'reviewers',
    title: '评审成员',
    itemKey: 'id',
    minItems: 1,
    maxItems: 5,
    fields: [
      { key: 'name', path: 'name', label: '姓名', required: true },
      { key: 'role', path: 'role', label: '角色', type: 'select' },
    ],
    createItem: () => ({ id: crypto.randomUUID(), name: '', role: 'owner' }),
  },
]
```

组件会根据 `addable`、`removable`、`minItems` 和 `maxItems` 控制按钮；也可以通过暴露的 `addGroup(groupKey)` 和 `removeGroup(groupKey, index)` 主动操作。分组变化会触发 `group-add` 和 `group-remove` 事件。

## 事件和暴露方法

- `submit(model, event?)`：校验成功后的提交事件。
- `validate({ valid, errors? })`：每次显式校验后的结果。
- `reset(model)`：恢复 `initialValues` 并清理校验状态；未提供 `initialValues` 时只恢复校验状态。
- `group-add` / `group-remove`：动态分组变化事件。
- `validate()`：执行标准校验并返回 `Promise<boolean>`。
- `submit()`：执行校验并在成功后触发 `submit`。
- `restoreValidation()`：清理校验反馈。
- `addGroup()` / `removeGroup()`：操作动态分组。
- `getFormInst()`：获取底层 Naive UI `FormInst`。
- `getModel()`：获取当前 model。

默认操作按钮可以通过 `showActions`、`showReset`、`submitText` 和 `resetText` 配置；需要完全自定义操作区时使用 `actions` 插槽。

## 演示入口

认证后打开 `/demo/features/form`，可以看到完整的布局配置、内置字段、自定义备注字段、动态评审成员、校验失败拦截、Loading 防重复提交、重置和提交结果预览。
