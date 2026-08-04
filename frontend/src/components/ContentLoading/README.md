# ContentLoading 使用文档

`ContentLoading` 是布局内部的内容区 Loading。它只在 `useRouteLoadingStore` 的 `scope === 'content'` 且 `loadingAnimation` 开启时显示，不遮挡侧边栏、顶部栏和标签页。

## 挂载方式

```vue
<div class="content-container">
  <ContentLoading />
  <RouterView />
</div>
```

承载容器必须具有定位上下文，例如 `position: relative`，组件会覆盖容器的整个区域。

## 状态来源

- `useRouteLoadingStore.start('content')` 开始内容区 Loading。
- `finish()` 完成导航并在最短显示时间后隐藏。
- `usePreferencesStore.loadingAnimation` 控制是否显示 Lottie 动画。
- 动画数据使用仓库内的 `car-loading3-data.json`。

组件没有 Props、Events 或暴露方法。业务请求 Loading 不应直接复用该组件，应由页面使用自己的 `loading` 状态控制按钮或局部内容。
