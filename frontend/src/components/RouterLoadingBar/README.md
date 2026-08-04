# RouterLoadingBar 使用文档

`RouterLoadingBar` 使用 Naive UI `LoadingBarProvider` 展示路由顶部进度条，和 Lottie 全屏/内容区 Loading 相互独立。

## 挂载方式

```vue
<NLoadingBarProvider :loading-bar-style="loadingBarStyle">
  <RouterLoadingBar />
  <RouterView />
</NLoadingBarProvider>
```

应用中只应挂载一个实例，并且必须位于 `NLoadingBarProvider` 内。

## 显示条件

当 `usePreferencesStore.pageTransition` 为 `true` 时：

- 路由开始导航时调用 `loadingBar.start()`。
- 导航完成时调用 `loadingBar.finish()`。
- 路由异常时调用 `loadingBar.error()`。

组件还会等待首次导航完成，并在卸载时清理 Router 监听。关闭 `pageTransition` 只隐藏进度反馈，不会阻止路由导航。
