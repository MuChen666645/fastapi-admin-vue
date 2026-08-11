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

`AppForm` 的完整配置、动态分组和自定义字段用法见 [AppForm/README.md](./AppForm/README.md)。

`AppSearchForm` 的搜索字段、折叠条件、回车策略和动作区用法见 [AppSearchForm/README.md](./AppSearchForm/README.md)。可访问 `/demo/features/form` 和 `/demo/features/search-form` 查看交互演示。

`AppUpload` 的文件列表绑定、拖拽触发、上传校验和生命周期事件见 [AppUpload/README.md](./AppUpload/README.md)。组件不绑定具体后端上传接口。

`AppUpdatePrompt` 由应用壳层统一挂载，负责轮询同源构建版本清单并提供整页刷新操作，详见 [AppUpdatePrompt/README.md](./AppUpdatePrompt/README.md)。

## 公共组件索引

| 组件                   | 用途                  | 说明                                                               |
| ---------------------- | --------------------- | ------------------------------------------------------------------ |
| `AppBreadcrumb`        | 路由面包屑            | [AppBreadcrumb/README.md](./AppBreadcrumb/README.md)               |
| `AppForm`              | 标准提交表单          | [AppForm/README.md](./AppForm/README.md)                           |
| `AppSearchForm`        | 标准搜索表单          | [AppSearchForm/README.md](./AppSearchForm/README.md)               |
| `AppUpload`            | 标准文件上传          | [AppUpload/README.md](./AppUpload/README.md)                       |
| `AppUpdatePrompt`      | 前端更新提示          | [AppUpdatePrompt/README.md](./AppUpdatePrompt/README.md)           |
| `ContentLoading`       | 布局内容区 Loading    | [ContentLoading/README.md](./ContentLoading/README.md)             |
| `DictTag`              | 字典值标签            | [DictTag/README.md](./DictTag/README.md)                           |
| `GlobalLoading`        | 全屏导航 Loading      | [GlobalLoading/README.md](./GlobalLoading/README.md)               |
| `MessageCenter`        | 消息中心列表展示      | [MessageCenter/README.md](./MessageCenter/README.md)               |
| `RequestMessageBridge` | 请求错误 Message 桥接 | [RequestMessageBridge/README.md](./RequestMessageBridge/README.md) |
| `RouterLoadingBar`     | 路由顶部进度条        | [RouterLoadingBar/README.md](./RouterLoadingBar/README.md)         |
| `WatermarkOverlay`     | 登录用户水印          | [WatermarkOverlay/README.md](./WatermarkOverlay/README.md)         |

除 `AppForm`、`AppSearchForm` 和 `AppUpload` 外，其余组件均为应用壳层组件，通常由 `App.vue` 或 `BasicLayout` 统一挂载，不建议在业务页面重复创建。`AppUpdatePrompt` 只应在 `App.vue` 挂载一次。

## 新增组件检查清单

1. 先确认组件是跨页面公共 UI，还是只服务一个页面；页面专属组件放在页面目录的 `components/`。
2. 明确 Props、Emits、Slots、`v-model` 和 `defineExpose` 的公开合同，相关类型从 `@/types` 导入。
3. 组件只处理展示、交互、局部校验和局部 Loading；提交事件交给页面或 Store 调用 `@/api`，组件不直接请求后端。
4. 覆盖空值、校验失败、禁用、重复提交、无权限展示和卸载清理等与组件公开行为相关的状态。
5. 在组件目录补充 README，在 `src/__tests__/` 补公开行为测试；复杂能力需要时接入认证后的静态演示路由。
