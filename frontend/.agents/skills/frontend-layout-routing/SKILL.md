---
name: frontend-layout-routing
description: 实现或评审 Vue 管理端静态和动态路由、BasicLayout、标签页、缓存、全屏或内容区 Loading、系统设置抽屉、导航和路由级页面组织。修改 frontend/src/router、layouts/BasicLayout、stores/modules/tabs、route-loading、layout-settings、preferences 或路由布局测试时使用。
---

# Frontend 布局与路由

用于维持受认证应用外壳、服务端动态路由、导航、缓存和 Loading 的职责边界。

## 工作流程

1. 读取 `src/router/`、`src/layouts/BasicLayout/`、相关 Store、路由页面和现有路由/布局测试。
2. 区分静态公共路由、静态认证路由、后端动态业务路由、隐藏跳转路由和不产生路由的系统设置
   抽屉；不得把抽屉或通用布局偏好放回 `src/views/`。
3. 动态路由经 `registerAuthenticatedRoutes()` 添加到 `app`，并只允许 `route-utils.ts` 中
   `import.meta.glob('../views/**/*.vue')` 白名单可解析的组件。
4. 保持标签、缓存、路由 Loading 和页面滚动彼此独立。`meta.noCache === false` 才允许缓存，
   缓存名沿用 `RouteTab_<route-key>`。
5. 使用 `useRouteLoadingStore` 选择 Loading 范围：进入或离开 `app` 使用 `screen`；`app` 内页
   面切换使用内容区 Loading；缓存切换不得重复展示。内容区 Loading 必须由 `BasicLayout` 限定
   在稳定内容容器内，不能随业务页面高度伸缩。
6. 系统设置仅由 `SystemSettingsDrawer` 在右侧抽屉呈现，保持滚动、可访问性、偏好持久化和布局
   响应式行为一致。
7. 对导航、动态路由过滤、缓存、标签关闭/刷新、Loading 范围和抽屉状态增加聚焦测试。

## 质量边界

- 不为路由便利新增未核验的后端菜单、组件路径、权限码或伪造页面。
- 不使路由缓存、标签或 Loading 改变认证、API、租户或数据范围。
- 不在布局中直接发起领域 API，路由页面继续通过类型化 API 层访问数据。
- 图标按钮提供可访问名称；功能图标使用静态 Ionicons5 导入。

详细检查项见 [layout-routing-checklist.md](references/layout-routing-checklist.md)。
