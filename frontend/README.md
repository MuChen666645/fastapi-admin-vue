# FastAPI Admin Vue 前端

这是 FastAPI Admin 的 Vue 3 管理前端，负责登录态、后端菜单路由、管理页面、标签页、主题和路由 Loading 交互。认证、授权、租户、数据范围和业务状态由 FastAPI 服务端最终决定。

English documentation: [README.en.md](./README.en.md).

## 技术栈

- Vue 3 + `<script setup lang="ts">` + TypeScript strict
- Vite + Vue Router + Pinia
- Alova fetch adapter + Naive UI
- UnoCSS reset、Sass、Ionicons 5
- Lottie Web、Vitest、Vue Test Utils、ESLint、Stylelint、Prettier

包管理器为 pnpm，Node 版本以 `package.json` 的 `engines` 为准。

## 快速开始

```sh
pnpm install
pnpm dev
```

默认开发服务为 `http://127.0.0.1:5173`。`pnpm dev` 会先执行 `pnpm run check`，检查通过后才启动 Vite。

开发环境默认将 `/api` 代理到 `http://127.0.0.1:3000`。如果 FastAPI 服务地址不同，复制 `.env.example` 为 `.env.local` 后修改 `VITE_API_PROXY_TARGET`，不要把密钥、Token 或内部凭据写入环境文件。

## 环境变量

| 变量                                              | 用途                      | 示例                         |
| ------------------------------------------------- | ------------------------- | ---------------------------- |
| `VITE_APP_TITLE`                                  | HTML 标题和页脚名称       | `FastAPI Admin`              |
| `VITE_API_BASE_URL`                               | 浏览器请求的 API 基础路径 | `/api/v1`                    |
| `VITE_API_PROXY_TARGET`                           | 开发代理目标              | `http://127.0.0.1:3000`      |
| `VITE_API_PROXY_ENABLED`                          | 是否启用 `/api` 代理      | `true`/`false`               |
| `VITE_DEV_HOST`、`VITE_DEV_PORT`、`VITE_DEV_OPEN` | 开发服务配置              | `127.0.0.1`、`5173`、`false` |
| `VITE_PREVIEW_HOST`、`VITE_PREVIEW_PORT`          | preview 服务配置          | `127.0.0.1`、`4173`          |
| `VITE_BASE_PATH`                                  | 部署基础路径              | `/`                          |
| `VITE_SOURCEMAP`                                  | 是否生成 sourcemap        | `false`                      |

项目不使用 `VITE_ROUTE_MODE`。登录后业务路由始终通过后端 `/api/v1/user/routes` 获取。

## 路由和权限

静态路由位于 `src/router/modules/`：

- `/login`：公开登录页。
- `/change-password`：认证后的密码修改页。
- `/`：`BasicLayout` 应用布局。
- `/system/settings`：统一系统设置入口，路由名为 `system-settings`，不作为后端菜单显示。
- `/demo/default-pages`：认证后的静态菜单，层级为“演示 / 缺省页 / 403、404、500、网络离线”，显示在前端侧边栏中。
- `/403`、`/500`、`/offline` 和 not-found：缺省页，统一提供刷新页面和返回首页操作。

登录后，前端调用 `GET /api/v1/user/routes`，将服务端返回的业务路由注册到 `app` 布局下。后端 `component` 会映射到本地 `src/views/**/*.vue`，支持以下形式：

```text
home/index
@/views/home/index.vue
../views/home/index.vue
./views/home/index.vue
/views/home/index.vue
```

路径和路由名称会先经过运行时校验。找不到本地组件的路由会被过滤，并在控制台输出一次警告；前端不把路由菜单当作后端授权替代品。

在线用户页面由后端动态菜单注册，按数据权限分页展示活跃登录会话，支持用户名和登录 IP 筛选。`monitor:online:forceLogout` 权限提供单会话下线和指定用户全部可见会话下线，两种操作都会二次确认。

## 目录结构

```text
src/
├── api/                 # 领域 API 和响应解析
├── components/          # 公共表单、Loading、请求 Message 桥、面包屑和路由反馈组件
├── hooks/               # 主题、语言、标题、Lottie、ECharts 和路由缓存等可复用行为
├── layouts/BasicLayout/ # 侧边栏、头部、标签页、内容区和页脚
├── router/              # 静态路由、认证守卫、动态路由转换
├── stores/modules/      # auth、tabs、route-loading、preferences
├── types/               # API、路由、Store、传输和 Lottie 类型
├── utils/               # 公共工具包、传输边界、运行时守卫和 Lottie 基础封装
├── views/               # 路由级页面
└── __tests__/           # Vitest 单元与组件测试
```

缺省页演示使用 `src/router/modules/protected.ts` 中的嵌套路由，四个叶子节点直接复用 `src/views/error/` 下的 403、404、500 和离线页面。

大页面的业务区域放在页面目录的 `components/` 中，例如 `src/views/system/config/components/`。公共组件才放入 `src/components/`。所有 `type`、`interface`、`enum` 声明统一放在 `src/types/`，通过 `@/types` 导入；新增普通样式优先使用 UnoCSS utility class。`src/views/` 下目录使用能表达业务域和页面职责的语义化名称。

## 组件、工具函数和 Hooks 开发约定

按依赖选择代码位置：

| 需求                | 目录                                    | 主要职责                                              | 不应承担                                     |
| ------------------- | --------------------------------------- | ----------------------------------------------------- | -------------------------------------------- |
| 跨页面 UI           | `src/components/`                       | 展示、交互、Props/Emits、插槽和局部校验               | 领域 API、业务列表、Token 和跨页面业务状态   |
| 页面专属 UI         | `src/views/<domain>/<page>/components/` | 当前页面的展示和交互编排                              | 被无关页面直接依赖，或重复实现公共组件       |
| 生命周期/上下文行为 | `src/hooks/use*.ts`                     | Vue 生命周期、Router、Pinia、DOM Ref 和第三方实例编排 | 领域 API、后端响应解析和业务提交             |
| 无生命周期逻辑      | `src/utils/`                            | 纯计算、格式化、解析、转换和安全校验                  | 隐式全局状态、页面副作用和未经说明的业务修改 |
| 跨页面业务状态      | `src/stores/modules/`                   | 会话、标签页、偏好和 Loading 状态                     | DOM、页面组件和后端授权替代                  |

组件通过 Props、Emits、`v-model` 或插槽交付数据和状态；提交表单或搜索时，组件先完成局部校验，再由页面或 Store 调用已核实的 `@/api`。新增公共组件必须维护组件目录 README 和 `src/__tests__/` 测试，记录 Props、Emits、Slots、暴露方法、校验/Loading 状态和最小示例。

Hook 统一使用 `use` 命名，只在需要 Vue/Router/Pinia/DOM 上下文时使用；所有监听器、订阅、观察器、定时器和第三方实例都必须在卸载时清理。工具函数默认保持无生命周期和明确输入输出，公共函数从 `@/utils` 导出；请求传输、响应守卫、存储和反馈桥等基础设施使用具体模块入口。

详细索引：[`src/components/README.md`](./src/components/README.md)、[`src/hooks/README.md`](./src/hooks/README.md)、[`src/utils/README.md`](./src/utils/README.md)。Codex 强制规则、架构边界和验证流程见 [`.codex/README.md`](./.codex/README.md)。

## 偏好配置与双语模式 / Preferences and bilingual mode

系统设置入口为 `/system/settings`，配置由 `usePreferencesStore` 统一管理，并通过 `localStorage` 持久化。设置包括：

- 外观：浅色、深色或跟随系统主题，主题色，圆角，字体大小，色弱和灰度模式。
- 布局：全屏或居中内容，侧边栏、标签页、面包屑、页脚，以及内容区固定方式。
- 通用：`zh-CN` / `en-US`、时区、动态标题、水印、更新检查开关和页面 Loading 开关。

内容区固定方式有三种：`content` 让顶部栏、标签栏和侧边栏固定、仅内容区内部滚动；`workspace` 让右侧工作区整体滚动；`sticky` 仅固定顶部栏和标签栏，其余右侧内容滚动。语言切换即时影响设置页和公共壳层，动态后端菜单标题在没有词典映射时保留服务端原文。

顶部栏和登录页顶部工具区提供语言切换按钮，可在不进入系统设置的情况下直接切换 `zh-CN` / `en-US`；首页统计、图表和活动文案会随偏好语言同步更新。

The `/system/settings` page is backed by one `usePreferencesStore` and persists preferences in `localStorage`. It covers appearance, layout, language, timezone, dynamic titles, watermark, update checking, and loading feedback. The three scroll modes are `content`, `workspace`, and `sticky`, matching the behavior described above. The bilingual UI supports `zh-CN` and `en-US`; static shell titles are translated and unknown backend titles are preserved.

The app header and login-page toolbar include a language toggle, so users can switch between `zh-CN` and `en-US` without opening system settings. Dashboard cards, charts, and activity copy follow the selected preference.

“定时检查更新”控制应用壳层对同源 `version.json` 的轮询。正式构建会生成唯一构建 ID，发现版本变化后显示更新提示；用户点击“立即刷新”才会执行整页刷新。该清单属于前端部署元数据，不依赖后端业务接口。复制偏好设置只包含本地 UI 配置，不包含 Token、密码或用户会话凭据。

The update-check switch controls polling of the same-origin `version.json` file used by the application shell. Production builds generate a unique build ID; when it changes, the app shows an update prompt, and a full reload occurs only after the user clicks “Refresh now”. This deployment metadata does not depend on a business API. Copying preferences exports UI settings only and never session credentials.

## 认证与 API

API 调用统一经过 `src/api/<domain>/index.ts` 和 `src/utils/request.ts`。当前认证相关接口包括：

```text
POST /user/login/username
POST /user/login/phone
GET  /captcha/image
POST /user/token/refresh
POST /user/logout
PUT  /user/me/password
GET  /user/info
GET  /user/routes
```

统一响应通常为 `{ code, error_code?, message, data }`。API parser 从 `unknown` 校验字段后才交给 Store 或页面。401 会由传输层使用共享刷新请求重试一次，失败后清理会话；普通请求异常通过 Naive UI Message 提示，登录和退出使用 Notification 提示。

## Loading、标签页和缓存

- 初始导航和布局外页面使用 `GlobalLoading` 全屏 Lottie 动画。
- `BasicLayout` 内部页面切换使用 `ContentLoading`，只覆盖内容区，不遮挡侧边栏、顶部栏和标签页。
- `RouterLoadingBar` 使用 Naive UI 顶部进度条。
- 通用设置中的 `pageTransition` 控制顶部进度条，`loadingAnimation` 控制全屏和内容区 Lottie；关闭后导航状态仍正常完成，只隐藏对应反馈。
- `meta.noCache === false` 的页面允许 KeepAlive 缓存，缓存名为 `RouteTab_<route-key>`。
- tabs 列表由 `useTabsStore` 使用 `sessionStorage` 持久化；组件缓存和标签列表是两个独立状态。

公共组件说明见 [`src/components/README.md`](./src/components/README.md)，Hook 使用说明见 [`src/hooks/README.md`](./src/hooks/README.md)，工具包说明见 [`src/utils/README.md`](./src/utils/README.md)。Lottie 基础函数位于 `src/utils/lottie.ts`，生命周期封装位于 `src/hooks/useLottie.ts`，动画数据位于 `src/assets/lottie/car-loading3-data.json`。

## 常用命令

```sh
pnpm run check             # 类型、ESLint、Stylelint、Prettier
pnpm run test:run          # 检查后运行全部 Vitest
pnpm run build             # 检查后构建 production 到 dist/
pnpm run build:staging     # 构建 staging 到 dist-staging/
pnpm run preview           # 检查后预览 production 构建
git diff --check           # 检查差异中的空白错误
```

定向测试示例：

```sh
pnpm exec vitest run src/__tests__/DynamicRouter.spec.ts
pnpm exec vitest run src/__tests__/Lottie.spec.ts
pnpm exec vitest run src/__tests__/SystemConfig.spec.ts
```

Windows 下如果 Vite/Vitest 报 `spawn EPERM`，需要在允许子进程的环境重试，并分别报告静态检查和运行时测试结果。

## 安全注意事项

- 不把 Token、密码、验证码、MFA、密码重置令牌和生产数据写入日志、URL、源码、截图或测试输出。
- 服务端路由组件只允许映射到本地 View 白名单，不允许根据服务端字符串任意导入组件。
- 当前用户主动选择记住登录时，`src/utils/loginPreferences.ts` 会将账号和密码写入 `localStorage`，这是已知风险；新功能不得扩大该行为，后续应单独进行安全整改。

## Codex 文档

前端规则和事实文档位于 `.codex/`：

- `AGENTS.md`：强制实现规则。
- `PROJECT.md`：当前项目事实、脚本、环境和接口。
- `ARCHITECTURE.md`：模块职责、路由、会话、缓存和 Loading 数据流。
- `BOUNDARY.md`：修改范围、安全边界和禁止事项。
- `WORKFLOW.md`：任务分析、实现、验证和交付流程。
- `PROMPTS/feature.md`、`PROMPTS/bugfix.md`：任务输入和交付模板。
