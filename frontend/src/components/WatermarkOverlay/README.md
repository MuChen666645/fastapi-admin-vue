# WatermarkOverlay 使用文档

`WatermarkOverlay` 在已认证的应用页面上显示当前用户名称水印，用于提示页面归属。水印覆盖整个窗口但不拦截点击，也不会写入路由、请求或业务数据。

## 挂载方式

```vue
<div class="app-root">
  <WatermarkOverlay />
  <RouterView />
</div>
```

组件通常由 `App.vue` 统一挂载。

## 显示条件

只有同时满足以下条件才渲染：

- `usePreferencesStore.watermark === true`。
- `useAuthStore.isAuthenticated === true`。

水印内容来自 `auth.displayName`。组件使用 `pointer-events: none` 和 `aria-hidden="true"`，不应在水印组件中放置交互控件或敏感信息。
