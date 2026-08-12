# ContentLoading 使用文档

`ContentLoading` 是布局内部的内容区 Loading。它只在 `useRouteLoadingStore` 的 `scope === 'content'` 且 `loadingAnimation` 开启时显示，不遮挡侧边栏、顶部栏、标签页和页脚。

组件由 `BasicLayout` 挂载在独立的 `content-loading-viewport` 中。该宿主固定为右侧工作区的可视高度，与业务页面内容高度解耦，因此长页面、空页面和三种滚动模式不会拉伸或收缩遮罩。

## 挂载方式

```vue
<div class="main-layout-shell">
  <NLayout class="main-layout">
    <RouterView />
  </NLayout>
  <div class="content-loading-viewport">
    <ContentLoading />
  </div>
</div>
```

`main-layout-shell` 必须保持稳定的视口高度并提供定位上下文。`content-loading-viewport` 作为 `main-layout` 的同级覆盖层，不能放入随页面内容增高的 `content-container` 或 `layout-content__body`。

## 状态来源

- `useRouteLoadingStore.start('content')` 开始内容区 Loading。
- `finish()` 完成导航并在最短显示时间后隐藏。
- `usePreferencesStore.loadingAnimation` 控制是否显示 Lottie 动画。
- 动画数据使用仓库内的 `car-loading3-data.json`。

组件没有 Props、Events 或暴露方法。业务请求 Loading 不应直接复用该组件，应由页面使用自己的 `loading` 状态控制按钮或局部内容。
