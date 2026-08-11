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
│   ├── AppBreadcrumb/、AppForm/、AppSearchForm/、AppUpload/、AppUpdatePrompt/
│   ├── ContentLoading/、GlobalLoading/、WatermarkOverlay/
│   ├── RequestMessageBridge/、RouterLoadingBar/
│   └── README.md
├── hooks/
│   ├── useAppUpdate.ts、useDocumentTitle.ts、useECharts.ts、useLocale.ts
│   ├── useLottie.ts、useRouteCache.ts、useTheme.ts
│   ├── index.ts
│   └── README.md
├── layouts/BasicLayout/
├── router/
│   ├── guards/auth.ts
│   ├── modules/public.ts、protected.ts、error.ts
│   ├── route-cache.ts、route-source.ts、route-utils.ts
│   └── index.ts
├── stores/modules/
│   ├── auth.ts、tabs.ts、route-loading.ts、preferences.ts、layout-settings.ts
│   ├── dictionary.ts
│   └── index.ts
├── types/
├── utils/
│   ├── index.ts、app-update.ts、icon.ts、i18n.ts、lottie.ts、preferences.ts、route-menu.ts
│   ├── request.ts、request-feedback.ts、loginPreferences.ts
│   └── guards/api.ts、route.ts
├── views/
└── __tests__/
```

`src/views/system/config/` 是系统设置页面，外观、布局、通用设置和标签切换组件位于该页面目录的 `components/` 下；`src/views/system/dict/data.vue` 是不显示菜单、由字典类型页跳转的认证静态页面；`src/views/system/message/` 是后端消息中心动态路由的收件箱和消息管理页面；顶栏 `useMessagePopover` 每 30 秒轮询最新消息并对新增未读站内信显示 `Notification`；类型声明统一位于 `src/types/` 的语义化领域文件中。

公共代码文档与源码保持同目录维护：`src/components/README.md` 记录公共组件索引和提交边界，组件组 README 记录各自公开 API；`src/hooks/README.md` 记录 Hook 的上下文依赖、返回值和清理行为；`src/utils/README.md` 记录公共工具入口、基础设施边界和安全校验。新增或迁移代码时，目录、公共出口、类型、测试和 README 必须同步。

## 偏好配置与双语模式 / Preferences and bilingual mode

`usePreferencesStore` 是偏好配置的唯一运行时来源，使用 `localStorage` 持久化外观、布局和通用配置。`useLayoutSettingsStore` 只是兼容旧调用方的导出别名，不再拥有第二份布局状态。偏好字段包含主题模式、强调色、圆角、字体大小、色弱/灰度、语言、时区、动态标题、水印、更新检查、页面反馈，以及内容宽度、导航可见性和滚动模式。

`zh-CN` 和 `en-US` 由 `src/utils/i18n.ts` 提供词典，纯工具通过 `src/utils/index.ts` 的 `@/utils` 入口复用；`useLocale` 暴露给设置页和公共壳层。静态路由标题由 `translateRouteTitle` 翻译；未收录的后端动态标题保持服务端原文。`dynamicTitle` 控制浏览器标题，`watermark` 只在已认证用户的工作区显示姓名水印。

`content`、`workspace`、`sticky` 分别表示内容区内部滚动、右侧工作区整体滚动、仅顶部栏和标签栏固定。`pageTransition` 控制顶部进度条，`loadingAnimation` 控制全屏和内容区 Lottie。`autoUpdate` 控制 `AppUpdatePrompt` 对同源 `version.json` 的轮询；该清单由 Vite 正式构建生成，不属于后端业务 API，检查失败不会阻断页面。

`usePreferencesStore` is the single runtime source for appearance, layout, and general preferences. `useLayoutSettingsStore` remains only as a compatibility alias. The UI dictionary supports `zh-CN` and `en-US`; static shell titles are translated, while unknown backend titles are preserved. Scroll modes are `content`, `workspace`, and `sticky`. The `autoUpdate` option controls polling of the Vite-generated same-origin `version.json` deployment manifest; failures do not block the page.

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

请求基于 `VITE_API_BASE_URL`，通常使用 `/api/v1` 前缀。`src/utils/request.ts` 使用 Alova fetch adapter，默认超时 15 秒，解析 `{ code, error_code?, message, data }` 响应，关闭请求缓存，并对 401 使用单飞刷新令牌逻辑。请求异常通过 `RequestMessageBridge` 使用 Naive UI Message 提示；登录和退出请求由页面使用 Notification 提示，避免重复弹窗。

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
| `GET`  | `/message/latest`              | 顶栏三类最新消息     |
| `GET`  | `/message/unread-count`        | 当前用户未读消息总数 |
| `GET`  | `/message/my/list`             | 当前用户消息分页     |
| `GET`  | `/message/my/{id}`             | 当前用户消息详情     |
| `POST` | `/message/{id}/read`           | 标记单条消息已读     |
| `POST` | `/message/read-all`            | 标记全部可见消息已读 |
| `GET`  | `/message/list`                | 当前租户消息管理分页 |
| `GET`  | `/message/{id}`                | 管理端消息详情       |
| `GET`  | `/dict/data/type/{dict_type}`  | 当前租户可用字典数据 |
| `POST` | `/message/add`                 | 发布消息并创建投递任务 |
| `PUT`  | `/message/{id}`                | 修改当前租户消息     |
| `DELETE` | `/message/{id}`              | 删除当前租户消息     |
| `GET`  | `/role/list`                  | 当前租户角色分页列表 |
| `GET`  | `/role/{id}`                  | 角色详情及菜单、部门关联 |
| `POST` | `/role/add`                   | 创建角色 |
| `PUT`  | `/role/{id}`                  | 修改角色 |
| `DELETE` | `/role/{id}`                | 删除角色 |
| `PUT`  | `/role/batch/status`          | 批量修改角色状态 |
| `GET`  | `/role/export`                | 导出角色 Excel |
| `POST` | `/role/import`                | 导入角色 Excel |
| `GET`  | `/menu/list`                  | 查询角色可配置的菜单树 |

认证响应保留后端字段 `access_token`、`refresh_token`、`token_type`、`expires_in`、`must_change_password`。路由响应保留 `path`、`name`、`component`、`redirect`、`hidden`、`meta` 和 `children`。

## 路由事实

- `/login` 是公开路由。
- `/change-password` 需要认证，并允许密码变更状态访问。
- `/` 对应 `app` 和 `BasicLayout`，认证后会注册后端业务路由。
- `/system/settings` 的路由名为 `system-settings`，是认证后的静态系统设置入口，不显示在后端菜单中。
- `/system/dict/data` 的路由名为 `system-dict-data`，是认证后的隐藏静态字典数据页，仅由字典类型页携带 `dict_type` 查询参数跳转，不显示在菜单中；守卫要求当前用户具有 `system:dict:list`。
- `/system/message` 来自后端消息中心菜单的动态路由，组件路径必须解析到 `src/views/system/message/index.vue`；页面包含当前用户收件箱和具有 `system:message:list` 权限时的租户消息管理模式。
- `/system/role` 来自后端角色管理菜单，组件路径解析到 `src/views/system/role/index.vue`；页面使用角色列表、详情和菜单/部门授权接口，并对角色写操作使用按钮权限指令。
- `/demo/default-pages` 是认证后的静态侧边栏菜单树，父级为 `demo`，子级为 `default-pages`，其下包含 `default-page-forbidden`、`default-page-not-found`、`default-page-server-error` 和 `default-page-offline` 四个叶子路由，不属于后端菜单。
- `/demo/features/form` 是认证后的表单组件演示页，菜单层级为 `demo -> features -> form`，用于展示通用 `AppForm` 的布局、自定义字段、标准校验、动态分组和规范提交；它不调用后端业务接口。
- `/demo/features/search-form` 是认证后的搜索表单组件演示页，菜单层级为 `demo -> features -> search-form`，用于展示通用 `AppSearchForm` 的搜索布局、条件折叠、自定义字段、回车策略、重置和查询状态；它不调用后端业务接口。
- `/demo/features/hooks` 是认证后的 Hooks 演示页，菜单层级为 `demo -> features -> hooks`，用于展示 `usePagination` 与 Naive UI `NDataTable` 内置分页的请求参数、加载状态、筛选重置和分页交互；它使用页面私有的本地异步适配器，不调用后端业务接口。
- `/demo/features/utils` 是认证后的工具函数演示页，菜单层级为 `demo -> features -> utils`，用于交互展示 `@/utils` 的 Moment 日期解析、格式化、locale、ISO 转换和日期范围能力；它不调用后端业务接口。
- `/403`、`/404`、`/500` 和 `/offline` 是公开缺省页面，统一提供刷新页面和返回首页操作，并使用 `src/assets/lottie/error/` 下的静态动画。
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
- `useDictionaryStore` 按类型缓存业务字典数据并合并并发请求；缓存不持久化，空数组也视为命中，退出登录和字典管理写操作会使其失效。
- `usePreferencesStore` 用 `localStorage` 持久化外观、通用和布局偏好；`useLayoutSettingsStore` 是兼容旧调用方的别名，默认固定布局并仅允许内容区内部滚动。
- `meta.noCache === false` 表示页面可缓存。`useRouteCache` 使用 `RouteTab_<route-key>` 包装组件，避免不同路由实例共享 KeepAlive 名称。
- `BasicLayout` 通过 `KeepAlive :include="cachedComponentNames"` 管理缓存；刷新当前标签会增加视图 key，保持标签列表但重新创建页面实例。

## Loading 与动画事实

- `src/utils/lottie.ts` 封装 `load/play/pause/destroy`，`src/hooks/useLottie.ts` 负责生命周期。
- `src/utils/icon.ts` 提供静态 Ionicons5 图标解析，纯公共工具从 `@/utils` 导入；它不是 Vue Hook。
- `GlobalLoading` 监听 Router 导航：初始导航和布局外导航使用全屏范围，布局内非缓存导航切换为内容范围。
- `ContentLoading` 放在 `BasicLayout` 内容区，只有 `route-loading` Store 的 scope 为 `content` 时显示。
- `RouterLoadingBar` 使用 Naive UI LoadingBarProvider 展示顶部进度。
- `route-loading` Store 以 240ms 作为最短显示时间，减少快速导航造成的闪烁。

## 已知风险

- `src/utils/loginPreferences.ts` 在用户选择记住登录时将 identifier 和 password 写入 `localStorage`。这属于敏感数据持久化风险；新功能不得扩大该模式，后续应单独评审替代方案。
- production 构建可能报告 `lottie-web` 第三方代码使用 direct `eval` 以及大 chunk 警告；它们不是当前前端源码的 lint 错误。
