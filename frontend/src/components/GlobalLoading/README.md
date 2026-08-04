# GlobalLoading 使用文档

`GlobalLoading` 是应用级全屏导航 Loading，负责初始导航、布局外页面切换和路由错误后的清理。进入 `app` 布局内部的页面时，它会切换为 `ContentLoading`，避免覆盖已经稳定的应用壳层。

## 挂载方式

```vue
<NConfigProvider>
  <GlobalLoading />
  <RouterView />
</NConfigProvider>
```

应用中只应挂载一个实例，通常由 `App.vue` 在 Provider 内统一挂载。

## 显示条件

组件同时依赖：

- `useRouteLoadingStore.visible`。
- `useRouteLoadingStore.scope === 'screen'`。
- `usePreferencesStore.loadingAnimation`。

组件会注册 Router 的 `beforeEach`、`afterEach` 和 `onError` 回调，并在卸载时解除注册、销毁动画和重置 Loading 状态。不要在业务页面重复注册相同的路由监听。
