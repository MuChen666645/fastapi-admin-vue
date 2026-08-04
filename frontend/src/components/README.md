# 组件组使用约定

`src/components/` 存放跨页面复用的界面组件。组件只负责 UI、交互和局部校验，不直接请求后端，不读取业务 Store，也不保存 Token、密码或业务数据。

## 目录约定

- 每个组件组使用独立目录，例如 `AppForm/`、`GlobalLoading/`。
- 组件入口使用 `index.vue`。
- 组件对外使用的 `type`、`interface` 和 `enum` 放在 `src/types/`，并从 `@/types` 导入。
- 组件级回归测试放在 `src/__tests__/`，测试公开行为而不是内部实现。
- 可复用组件组必须在自身目录维护 `README.md`，说明用途边界、API、插槽、暴露方法、状态约定和示例。
- 组件需要展示复杂能力时，在认证后的静态演示菜单中提供可操作的示例页面。

## 提交边界

通用组件通过事件向页面交付已经校验的数据。页面负责调用领域 API、处理成功/失败反馈和维护请求 Loading：

```vue
<AppForm :model="form" :loading="submitting" @submit="handleSubmit" />
```

```ts
const handleSubmit = async (model: FormModel): Promise<void> => {
  submitting.value = true
  try {
    await saveForm(model)
  } finally {
    submitting.value = false
  }
}
```

`AppForm` 的完整配置、动态分组和自定义字段用法见 [AppForm/README.md](./AppForm/README.md)。可直接访问 `/demo/features/form` 查看交互演示。
