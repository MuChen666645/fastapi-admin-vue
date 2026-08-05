# AppUpdatePrompt

`AppUpdatePrompt` 是应用壳层的前端版本更新提示。它通过构建产物中的同源 `version.json` 检查当前构建 ID，发现版本变化后显示刷新操作。

## 挂载方式

组件依赖 `usePreferencesStore` 和 `useLocale`，应在 `App.vue` 中只挂载一个实例。`autoUpdate` 为 `false` 时不会启动检查定时器。

```vue
<AppUpdatePrompt />
```

## 行为约定

- 正式构建会生成 `version.json`，不依赖后端业务接口。
- 默认首次挂载立即检查，之后每 5 分钟检查一次。
- 检查失败不会打断页面使用，也不会显示错误提示。
- 用户点击“立即刷新”才会执行 `window.location.reload()`。
- 提示可以关闭；同一页面生命周期内不会重复显示同一个更新提示。
