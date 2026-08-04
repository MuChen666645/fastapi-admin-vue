# AppSearchForm 使用文档

`AppSearchForm` 是面向列表筛选场景的标准搜索表单组件。它复用 `AppForm` 的字段 schema、Naive UI 校验和字段插槽，并补充搜索表单常用的折叠、展开、回车搜索、重置、Loading 防重复提交和动作区布局。

组件不请求 API，也不保存列表数据。搜索成功后通过 `@search` 交给页面或领域 Store 调用已经核实的查询接口。

## 基础用法

```vue
<script setup lang="ts">
import { reactive, ref } from 'vue'

import AppSearchForm from '@/components/AppSearchForm/index.vue'
import type { AppFormField } from '@/types'

interface UserQuery {
  keyword: string
  status: string | null
  owner: string | null
}

const query = reactive<UserQuery>({ keyword: '', status: null, owner: null })
const loading = ref(false)
const fields: AppFormField[] = [
  { key: 'keyword', path: 'keyword', label: '关键词', componentProps: { clearable: true } },
  {
    key: 'status',
    path: 'status',
    label: '状态',
    type: 'select',
    componentProps: {
      clearable: true,
      options: [
        { label: '启用', value: 'enabled' },
        { label: '停用', value: 'disabled' },
      ],
    },
  },
  { key: 'owner', path: 'owner', label: '负责人', type: 'select' },
]

const handleSearch = async (model: UserQuery): Promise<void> => {
  loading.value = true
  try {
    // 在此调用当前业务中已经核实的列表查询 API。
    void model
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <AppSearchForm
    :model="query"
    :fields="fields"
    :loading="loading"
    default-collapsed
    :collapsed-fields="2"
    @search="handleSearch"
  />
</template>
```

只有通过 `NForm.validate()` 的条件才会触发 `search`。`loading` 为 `true` 时，搜索、重置、折叠按钮和字段控件都会进入禁用状态，避免重复提交或改变正在请求的条件。

## 布局配置

`layout` 继承 `AppFormLayout`，默认适合后台列表筛选：左侧标签、88px 标签宽度、响应式三列栅格和 20px 横向间距。

```vue
<AppSearchForm
  :model="query"
  :fields="fields"
  :layout="{
    labelPlacement: 'top',
    labelWidth: 'auto',
    columns: '1 s:2 m:4',
    responsive: 'screen',
    xGap: 16,
    yGap: 12,
    actionAlign: 'end',
  }"
/>
```

`actionAlign` 支持 `start`、`center` 和 `end`。字段的 `span` 仍然可以覆盖单个字段在栅格中的占位列数。

## 折叠与展开

- `defaultCollapsed`：非受控模式的初始状态。
- `collapsed`：受控模式的当前状态，可配合 `v-model:collapsed` 使用。
- `collapsedFields`：折叠时保留展示的字段数量，默认为 `3`。
- `showToggle`：是否显示展开/收起按钮；字段数量未超过 `collapsedFields` 时自动隐藏。
- `@toggle` / `@update:collapsed`：监听折叠状态变化。

折叠只影响字段渲染，不会删除或清空隐藏条件；展开后可以继续编辑，点击搜索时 model 会包含所有已经填写的条件。

## 自定义字段与动作区

字段插槽名称为 `field-${field.key}`，参数与 `AppForm` 一致，包含 `value`、`model`、`path` 和 `setValue`：

```vue
<AppSearchForm :model="query" :fields="fields">
  <template #field-keyword="{ value, setValue }">
    <NInput
      :value="typeof value === 'string' ? value : ''"
      clearable
      placeholder="搜索名称、编码或邮箱"
      @update:value="setValue"
    />
  </template>
</AppSearchForm>
```

支持 `before`、`content` 和 `after` 插槽，用于放置筛选提示或自定义内容。需要完全控制按钮时使用 `actions` 插槽：

```vue
<template #actions="{ loading, disabled, canToggle, collapsed, search, reset, toggle }">
  <NButton :disabled="disabled" @click="reset">清空条件</NButton>
  <NButton v-if="canToggle" :disabled="disabled" @click="toggle">
    {{ collapsed ? '更多条件' : '收起条件' }}
  </NButton>
  <NButton type="primary" :loading="loading" :disabled="disabled" @click="search()"> 查询 </NButton>
</template>
```

## 事件与暴露方法

- `search(model, event?)`：校验成功后的搜索事件。
- `reset(model)`：恢复 `initialValues` 或初始 model，并清理校验状态。
- `validate({ valid, errors? })`：转发每次显式校验结果。
- `toggle(collapsed)`：折叠状态发生变化。
- `update:collapsed`：受控折叠状态更新事件。
- `search()`：暴露方法，执行校验并触发搜索事件。
- `reset()`：暴露方法，恢复初始筛选条件。
- `toggle()`：暴露方法，切换折叠状态并返回新状态。
- `validate()`：暴露方法，执行标准校验并返回 `Promise<boolean>`。
- `restoreValidation()`：清理校验反馈。
- `getFormInst()` / `getModel()`：获取底层表单实例或当前 model。

默认情况下按回车会触发搜索；设置 `searchOnEnter="false"` 可以关闭回车搜索，但仍保留显式查询按钮和暴露方法。

## 演示入口

认证后打开 `/demo/features/search-form`，可以查看响应式布局、折叠条件、自定义字段、回车搜索、标准校验、重置、Loading 防重复提交、动作区插槽和本地结果预览。
