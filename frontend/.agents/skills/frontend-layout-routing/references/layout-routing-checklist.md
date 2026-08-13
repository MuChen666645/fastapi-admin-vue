# 布局与路由检查表

## 路由

- [ ] 已区分公开、认证、动态、隐藏和不产生路由的 UI。
- [ ] 动态组件仅从本地 `import.meta.glob('../views/**/*.vue')` 白名单解析。
- [ ] 无效组件路径、异常元数据和无权限静态路由有安全处理。
- [ ] 路由守卫、强制改密、回跳、动态注册和标签行为一致。

## 布局与 Loading

- [ ] 系统设置保持在 `layouts/BasicLayout/components/SystemSettingsDrawer/`。
- [ ] 进入/离开 `app` 使用全屏 Loading，内部导航使用内容区 Loading。
- [ ] 内容区 Loading 固定在布局内容容器，不受页面内容高度影响。
- [ ] 缓存、标签、滚动和 Loading 状态没有互相耦合。

## 验证

- [ ] 已运行相关路由、BasicLayout、Tabs、RouteCache、Loading 或抽屉测试。
- [ ] 涉及公共布局或构建资源时已运行 `pnpm run build`。
