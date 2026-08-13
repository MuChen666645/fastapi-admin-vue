# 前端项目事实

## 运行环境

- 应用位于 `frontend/`，是基于 Vite 构建、pnpm 管理的 Vue 3 单页应用；支持的
  Node 版本以 `package.json` 为准。
- `@` 指向 `src/`。领域请求通过 `src/utils/request.ts` 使用配置的 `/api/v1`
  基础地址。
- Naive UI 是组件库，UnoCSS 提供 utility 样式，Ionicons5 提供功能图标。

## 源码目录

| 位置 | 职责 |
| --- | --- |
| `src/api/<domain>/` | 请求编码与响应 Parser 校验 |
| `src/components/` | 可复用、展示导向的 UI |
| `src/hooks/` | 依赖 Vue、Router、Pinia 或 DOM 的复用行为 |
| `src/layouts/BasicLayout/` | 已认证应用外壳和系统设置抽屉 |
| `src/router/` | 静态路由、守卫和动态路由校验转换 |
| `src/stores/modules/` | 会话、偏好、字典、标签、消息和 Loading 状态 |
| `src/types/` | API、UI、路由、Store 和测试类型声明 |
| `src/utils/` | 纯工具及请求、守卫、存储和反馈基础设施 |
| `src/views/` | 路由级业务页面和路由局部组件 |
| `src/__tests__/` | 行为与契约导向的 Vitest 测试 |

## 已核验运行流程

- `useAuthStore` 通过 `@/api/auth` 接收令牌，通过 `@/api/user` 初始化当前用户和
  权限，再从 `GET /api/v1/user/routes` 加载服务端路由。
- 动态路由经校验后注册在 `app` 下；公开路由和静态认证路由保留在前端。
- `BasicLayout` 挂载右侧 `SystemSettingsDrawer`，它不是业务页面；服务端菜单对应
  的系统参数业务页面位于 `src/views/system/config/`。
- `useRouteLoadingStore` 区分壳层 `screen` Loading 和内容区 Loading；
  `ContentLoading` 固定在布局内容区，不随页面高度变化。

## 命令

| 命令 | 用途 |
| --- | --- |
| `pnpm run check` | TypeScript、ESLint、Stylelint、Prettier 检查 |
| `pnpm run test:run` | 静态检查后执行非 watch Vitest |
| `pnpm run build` | 静态检查后执行生产构建 |
| `pnpm run dev` | 静态检查后启动开发 Vite 服务 |

开发中先运行最小相关测试；交付前运行 `pnpm run check`、受影响测试和
`git diff --check`。涉及运行时打包行为或公共 UI 资源时运行生产构建。
