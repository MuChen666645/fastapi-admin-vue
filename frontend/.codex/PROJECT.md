# 前端项目事实

本文件只记录已从 `frontend/` 当前源码、配置、测试和 `package.json` 核对出的事实。它不是目标目录规划；如果事实变化，先核对源码再更新本文件。

## 项目定位

`frontend/` 是通过 HTTP 与 FastAPI 管理服务协作的 Vue 3 单页应用，负责登录态展示、后端菜单路由注册、管理页面、标签页和主题/Loading 交互。后端仍是认证、授权、租户、数据范围和业务状态的最终权威。

当前技术栈：

- Vue 3、TypeScript、Vite、Vue Router、Pinia、Alova、Naive UI。
- UnoCSS Vite 插件、`@unocss/reset`、Sass、SVG loader、Vite SVG icons。
- `@vicons/ionicons5`，Lottie 使用 `lottie-web`。
- Vitest、jsdom、Vue Test Utils、vue-tsc、ESLint、Stylelint、Prettier。
- 包管理器为 pnpm；Node 版本为 `^22.18.0 || >=24.12.0`。

## 当前目录

```text
src/
├── api/
│   ├── auth/index.ts、parsers.ts
│   ├── user/index.ts、parsers.ts
│   └── index.ts
├── components/
│   ├── AppBreadcrumb/
│   ├── ContentLoading/
│   ├── GlobalLoading/
│   └── RouterLoadingBar/
├── hooks/
│   ├── useECharts.ts、useIcon.ts、useLottie.ts
│   ├── useRouteCache.ts、useTheme.ts
│   └── index.ts
├── layouts/BasicLayout/
├── router/
│   ├── guards/auth.ts
│   ├── modules/public.ts、protected.ts、error.ts
│   ├── route-cache.ts、route-source.ts、route-utils.ts
│   └── index.ts
├── stores/modules/
│   ├── auth.ts、tabs.ts、route-loading.ts
│   └── index.ts
├── types/
├── utils/
├── views/
└── __tests__/
```

`src/views/system/config/` 是系统设置页面，外观、布局、通用设置和标签切换组件位于该页面目录的 `components/` 下；类型声明统一位于 `src/types/system-config.ts`。

## 构建与测试脚本

| 命令                         | 当前行为                                     |
| ---------------------------- | -------------------------------------------- |
| `pnpm run dev`               | 先运行 `check`，再启动 development Vite 服务 |
| `pnpm run dev:staging`       | 先运行 `check`，再以 staging mode 启动       |
| `pnpm run type-check`        | `vue-tsc --build`                            |
| `pnpm run lint`              | ESLint，禁止 warning                         |
| `pnpm run lint:style`        | Stylelint 检查 `src/**/*.{css,scss,vue}`     |
| `pnpm run format:check`      | Prettier 检查源码、配置和 README             |
| `pnpm run check`             | 类型、ESLint、Stylelint、Prettier 的组合检查 |
| `pnpm run test:run`          | 先运行 `check`，再执行 `vitest run`          |
| `pnpm run build`             | 先运行 `check`，再构建 production 到 `dist/` |
| `pnpm run build:development` | 构建到 `dist-development/`                   |
| `pnpm run build:staging`     | 构建到 `dist-staging/`                       |
| `pnpm run preview`           | 先运行 `check`，再预览 production 构建       |

`test`、`test:unit` 和 `test:unit:run` 是现有兼容别名；新文档和新任务优先使用 `pnpm run test:run`。

## 环境变量

环境声明位于 `env.d.ts`，示例位于 `.env.example`。当前变量：

| 变量                                              | 用途                     | 默认或示例                   |
| ------------------------------------------------- | ------------------------ | ---------------------------- |
| `VITE_APP_TITLE`                                  | HTML 标题和页脚应用名称  | `FastAPI Admin`              |
| `VITE_API_BASE_URL`                               | API 基础路径             | `/api/v1`                    |
| `VITE_API_PROXY_TARGET`                           | 开发代理目标             | `http://127.0.0.1:3000`      |
| `VITE_API_PROXY_ENABLED`                          | 是否启用 `/api` 开发代理 | 开发环境 `true`              |
| `VITE_DEV_HOST`、`VITE_DEV_PORT`、`VITE_DEV_OPEN` | Vite 开发服务            | `127.0.0.1`、`5173`、`false` |
| `VITE_PREVIEW_HOST`、`VITE_PREVIEW_PORT`          | Vite preview 服务        | `127.0.0.1`、`4173`          |
| `VITE_BASE_PATH`                                  | 静态部署基础路径         | `/`                          |
| `VITE_SOURCEMAP`                                  | 是否生成 sourcemap       | `false`                      |

项目不使用 `VITE_ROUTE_MODE`。登录后路由始终通过后端 `/user/routes` 加载。

## API 事实

请求基于 `VITE_API_BASE_URL`，通常使用 `/api/v1` 前缀。`src/utils/request.ts` 使用 Alova fetch adapter，默认超时 15 秒，解析 `{ code, error_code?, message, data }` 响应，并对 401 使用单飞刷新令牌逻辑。

当前领域 API：

| 方法   | 相对路径                       | 用途                 |
| ------ | ------------------------------ | -------------------- |
| `POST` | `/user/login/username`         | 用户名登录，表单编码 |
| `POST` | `/user/login/phone`            | 手机号登录，表单编码 |
| `GET`  | `/captcha/image?timestamp=...` | 获取图形验证码       |
| `POST` | `/user/token/refresh`          | 刷新令牌             |
| `POST` | `/user/logout`                 | 退出登录             |
| `PUT`  | `/user/me/password`            | 修改当前用户密码     |
| `GET`  | `/user/info`                   | 当前用户、角色和权限 |
| `GET`  | `/user/routes`                 | 当前用户可见路由     |

认证响应保留后端字段 `access_token`、`refresh_token`、`token_type`、`expires_in`、`must_change_password`。路由响应保留 `path`、`name`、`component`、`redirect`、`hidden`、`meta` 和 `children`。

## 路由事实

- `/login` 是公开路由。
- `/change-password` 需要认证，并允许密码变更状态访问。
- `/` 对应 `app` 和 `BasicLayout`，认证后会注册后端业务路由。
- `/system/settings` 的路由名为 `system-settings`，是认证后的静态系统设置入口，不显示在后端菜单中。
- 后端 `component` 会被标准化为 `src/views/<component>.vue`，支持 `home/index`、`@/views/home/index.vue`、`../views/home/index.vue` 等形式。
- 不安全路径、未知本地组件和没有可导航子节点的容器路由会被过滤；未知组件会在控制台打印一次警告。

## 前端代码约定

- 新增 CSS 优先使用 UnoCSS utility class；组件专属复杂样式才使用 `<style scoped>`。
- 所有 `type`、`interface`、`enum` 声明都放在 `src/types/`，通过 `@/types` 导入；禁止在 `views`、组件、Hook、Store、Router 或工具文件内声明类型。
- `src/views/` 下的目录名必须语义化并描述业务域或页面职责，且与后端 `component` 路径一致；页面私有组件使用对应页面的 `components/`，不创建 `views/common` 等无语义目录。
- 后端路由通过 `router.addRoute('app', route)` 注册，并由 `clearAuthenticatedRoutes()` 清理动态注册项。

## 会话、标签页与缓存

- `useAuthStore` 管理访问令牌、刷新令牌、当前用户、权限、后端路由和 `AuthStatus`。
- auth Store 仅用 Pinia persisted state 的 `sessionStorage` 持久化 `refreshToken` 和 `rememberedUsername`。
- `useTabsStore` 用 `sessionStorage` 持久化 `tabs`，负责增加、关闭当前/其他/全部标签页。
- `meta.noCache === false` 表示页面可缓存。`useRouteCache` 使用 `RouteTab_<route-key>` 包装组件，避免不同路由实例共享 KeepAlive 名称。
- `BasicLayout` 通过 `KeepAlive :include="cachedComponentNames"` 管理缓存；刷新当前标签会增加视图 key，保持标签列表但重新创建页面实例。

## Loading 与动画事实

- `src/utils/lottie.ts` 封装 `load/play/pause/destroy`，`src/hooks/useLottie.ts` 负责生命周期。
- `GlobalLoading` 监听 Router 导航：初始导航和布局外导航使用全屏范围，布局内非缓存导航切换为内容范围。
- `ContentLoading` 放在 `BasicLayout` 内容区，只有 `route-loading` Store 的 scope 为 `content` 时显示。
- `RouterLoadingBar` 使用 Naive UI LoadingBarProvider 展示顶部进度。
- `route-loading` Store 以 240ms 作为最短显示时间，减少快速导航造成的闪烁。

## 已知风险

- `src/utils/loginPreferences.ts` 在用户选择记住登录时将 identifier 和 password 写入 `localStorage`。这属于敏感数据持久化风险；新功能不得扩大该模式，后续应单独评审替代方案。
- production 构建可能报告 `lottie-web` 第三方代码使用 direct `eval` 以及大 chunk 警告；它们不是当前前端源码的 lint 错误。
