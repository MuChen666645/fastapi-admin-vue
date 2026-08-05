# Hooks 使用文档

`src/hooks/` 存放依赖 Vue 生命周期、Router、Pinia 或组件上下文的可复用行为。所有 Hook 必须在组件的 `setup` 或 `<script setup>` 中调用，不负责直接请求 API，也不保存敏感数据。

## 公共入口

```ts
import { useECharts, useLocale, useLottie, useRouteCache, useTheme } from '@/hooks'
```

`useDocumentTitle` 通常只在 `App.vue` 调用；`useRouteCache` 只在 `BasicLayout` 使用。纯函数不放在 hooks 中，图标解析已迁移到 [工具包](../utils/README.md)。

## Hook 索引

| Hook               | 参数                                              | 返回值                                          | 适用场景                           |
| ------------------ | ------------------------------------------------- | ----------------------------------------------- | ---------------------------------- |
| `useDocumentTitle` | 无                                                | `void`                                          | 监听路由和语言，更新浏览器标题。   |
| `useECharts`       | `Ref<HTMLElement \| null>`、`() => EChartsOption` | `renderChart`                                   | 初始化、更新和销毁 ECharts。       |
| `useLocale`        | 无                                                | `language`、`t`                                 | 读取界面语言和类型安全的词典文案。 |
| `useLottie`        | 容器 Ref、动画数据、可选项                        | `animation`、`load`、`play`、`pause`、`destroy` | 管理 Lottie 生命周期。             |
| `useRouteCache`    | 无                                                | 缓存名称、组件包装和路由 key 方法               | BasicLayout 的 KeepAlive 缓存。    |
| `useTheme`         | 无                                                | `isDarkMode`、`naiveTheme`、`toggleTheme`       | 主题状态和主题切换。               |

## usePagination

`usePagination` 只负责分页状态、并发请求协调和 Naive UI 分页属性，不直接调用 API。页面应从领域 API 获取分页数据，再把请求函数传入 Hook。请求函数接收后端 `fastapi-pagination` 的 `{ page, size }` 参数，并返回 `{ items, total, page, size, pages }`。

```ts
import { usePagination } from '@/hooks'

const { items, loading, pagination, reset } = usePagination(
  (params) => fetchUserList({ ...filters, ...params }),
  { initialPageSize: 20 },
)
```

`pagination` 可直接绑定到 Naive UI 的 `NPagination`：

```vue
<NPagination v-bind="pagination" />
```

使用 `NDataTable` 的内置远程分页时，开启 `remote` 并把同一个绑定传给 `pagination`：

```vue
<NDataTable remote :data="items" :pagination="pagination" />
```

Hook 默认在组件挂载后加载第 1 页；传入 `immediate: false` 可改为手动调用 `load()`。切换页码会自动请求，切换页大小会回到第 1 页并请求。`reset()` 会恢复初始页码和页大小后请求，`reset({ reload: false })` 只恢复状态。`reload` 和 `refresh` 是 `load` 的语义别名。

`pagination` 使用 `itemCount` 驱动 Naive UI，不同时传入 `pageCount`，避免组件重复计算告警。后端返回数据为空但当前页已越界时，Hook 会自动请求最后一页；过期请求的结果不会覆盖较新的结果。`error` 仅保存当前请求错误，失败时保留已有列表数据，页面可据此展示重试操作。

## useDocumentTitle

```ts
import { useDocumentTitle } from '@/hooks'

useDocumentTitle()
```

它监听当前路由的 `meta.title`、`dynamicTitle` 和语言偏好。启用动态标题时，标题格式为“路由标题 | 应用名称”；关闭时只显示 `VITE_APP_TITLE`。没有 `document` 的 SSR 或测试环境会安全跳过。

## useECharts

```vue
<script setup lang="ts">
import { ref } from 'vue'
import type { EChartsOption } from 'echarts'

import { useECharts } from '@/hooks'

const chartElement = ref<HTMLElement | null>(null)
const option: EChartsOption = {
  xAxis: { type: 'category', data: ['一月', '二月'] },
  yAxis: { type: 'value' },
  series: [{ type: 'bar', data: [12, 18] }],
}

const { renderChart } = useECharts(chartElement, () => option)
</script>

<template><div ref="chartElement" class="chart" /></template>
```

Hook 在挂载后初始化 Canvas 图表，监听容器尺寸并在卸载前断开观察器、销毁实例。数据或主题变化后调用 `renderChart()`；不要在组件外保存 ECharts 实例。

## useLocale

```ts
import { useLocale } from '@/hooks'

const { language, t } = useLocale()
const title = t('sidebar.brand')
```

`language` 是响应式 `Ref<PreferenceLanguage>`，`t` 只处理前端静态文案。词典 key 必须使用 `TranslationKey`，后端业务数据、权限码、状态枚举和错误字段不能交给该 Hook 翻译。没有活跃 Pinia 时会回退为 `zh-CN`，适合测试和独立组件。

## useLottie

```ts
import { ref } from 'vue'

import loadingAnimation from '@/assets/lottie/car-loading3-data.json'
import { useLottie } from '@/hooks'

const container = ref<HTMLElement | null>(null)
const { play, pause, destroy } = useLottie(container, loadingAnimation, {
  autoplay: false,
  loop: true,
  renderer: 'svg',
})
```

Hook 会在挂载时创建动画，并在卸载时销毁实例。`animation` 是只读 Ref；`load`、`play`、`pause`、`destroy` 可以由组件交互调用。动画数据必须来自仓库内静态资源，不能传入外部脚本地址。

## useRouteCache

```ts
const { cachedComponentNames, getCachedRouteComponent, getRouteKey } = useRouteCache()
```

该 Hook 依赖 `useRoute` 和 `useTabsStore`，为可缓存路由生成 `RouteTab_<route-key>` 包装组件，避免不同路由共用组件名造成 KeepAlive 串缓存。它是布局基础设施，不应在普通业务页面自行创建另一套缓存。

## useTheme

```ts
const { isDarkMode, naiveTheme, toggleTheme } = useTheme()
```

`isDarkMode` 和 `naiveTheme` 是响应式值，`toggleTheme()` 会更新 `usePreferencesStore` 并持久化主题偏好。根组件负责把颜色、圆角、字体和无障碍模式同步到 CSS 变量；页面只需要读取返回值，不要直接修改主题 DOM class。

## 设计约束

- Hook 只封装可复用行为，不放领域 API 和业务提交逻辑。
- 所有生命周期监听必须在卸载时清理。
- 需要跨页面共享的数据放 Pinia Store，不通过模块级可变变量传递。
- 纯计算、格式化、解析和浏览器存储函数放入 `src/utils/`，从 [工具包入口](../utils/README.md) 了解导出范围。

## 新增或修改 Hook 检查清单

1. 只有依赖 Vue 生命周期、Router、Pinia、DOM Ref 或组件上下文的行为才放入 `src/hooks/`；纯函数放入 `src/utils/`。
2. Hook 使用 `use` 命名，返回值只暴露调用方需要的 Ref、Computed 和动作函数，不把内部实例作为隐式全局状态。
3. 记录依赖的 Router、Store、Provider 或浏览器能力，并为无 DOM、无 Pinia 和测试环境提供安全降级（如果当前行为需要）。
4. 为 Router 监听、事件监听、ResizeObserver、定时器和第三方实例建立成对的清理逻辑，重复挂载和卸载不能泄漏。
5. 不在 Hook 内调用领域 API、提交业务数据或持久化敏感信息；修改后同步 `hooks/index.ts`、本 README 和针对初始化/更新/清理的测试。
