# FastAPI Admin Vue

FastAPI Admin Vue 是 FastAPI Admin 的企业级管理前端，基于 Vue 3、TypeScript、Vite 和 Naive UI 构建。项目提供统一的认证会话、动态路由、权限菜单、管理工作台、主题偏好、国际化和导航反馈能力，并通过版本化 HTTP API 与 FastAPI 服务协作。

> 前端负责交互体验和权限展示，FastAPI 服务端始终是认证、授权、租户隔离、数据范围、业务状态和数据一致性的最终权威。

English documentation: [README.en.md](./README.en.md)

## 1. 项目定位

本项目面向企业后台、内部运营平台和多租户管理系统，重点关注以下工程目标：

- **契约明确**：所有业务调用通过领域 API 模块和独立 TypeScript 类型完成，不在页面中直接调用传输客户端。
- **权限闭环**：服务端下发路由和权限码，前端负责菜单、路由和操作可见性，后端负责最终鉴权。
- **体验一致**：统一布局、标签页、面包屑、搜索表单、数据表格、反馈、主题和 Loading 行为。
- **边界清晰**：页面、公共组件、Hook、Store、API 和工具函数各自承担单一职责。
- **可验证交付**：严格执行类型检查、代码规范、样式规范、格式检查、单元测试和生产构建。

## 2. 功能能力

| 领域           | 已实现能力                                                                      |
| -------------- | ------------------------------------------------------------------------------- |
| 认证与会话     | 用户名登录、图形验证码、Token 刷新、退出登录、修改密码、会话失效处理            |
| 路由与权限     | 服务端动态路由、本地组件白名单解析、认证守卫、权限码控制、静态与动态菜单合并    |
| 组织与权限管理 | 用户、角色、菜单、部门、岗位管理，角色菜单权限和数据范围配置                    |
| 基础数据       | 字典类型、字典数据、导入导出和字典展示组件                                      |
| 消息中心       | 消息管理、用户消息、未读统计、标记已读和顶部消息入口                            |
| 系统监控       | 登录日志、操作日志、异常日志、在线会话和强制下线                                |
| 定时任务       | 任务分页、详情、新增、修改、删除、立即执行和执行日志                            |
| 应用体验       | 多标签页、KeepAlive、主题与布局偏好、中英文、时区、水印、更新检测和路由 Loading |
| 公共能力       | 标准表单、搜索表单、文件选择与上传交互、分页、ECharts、Lottie 和通用工具函数    |

业务页面是否可见取决于服务端返回的菜单、当前用户权限和实际部署的后端能力。定时任务的 `task_name` 必须对应服务端已注册的任务处理器，前端不提供任意代码执行入口。

## 3. 技术栈

| 分类         | 技术                                                            |
| ------------ | --------------------------------------------------------------- |
| 核心框架     | Vue 3、`<script setup lang="ts">`、TypeScript Strict Mode       |
| 工程化       | Vite、pnpm、Sass、UnoCSS                                        |
| 路由与状态   | Vue Router、Pinia、`pinia-plugin-persistedstate`                |
| UI 与图标    | Naive UI、Ionicons 5、SVG Icon                                  |
| HTTP         | Alova Fetch Adapter                                             |
| 可视化与动画 | ECharts、Lottie Web                                             |
| 质量工具     | Vitest、Vue Test Utils、ESLint、Stylelint、Prettier、Commitlint |

Node.js 支持范围以 `package.json` 为准，当前为 `^22.18.0 || >=24.12.0`。项目统一使用 pnpm。

## 4. 架构概览

```text
View / Layout / Component
           │
           ├── Hook / Pinia Store
           │
           └── Domain API ── Response Parser
                              │
                         Request Transport
                              │
                         /api/v1 (FastAPI)
```

主要运行链路：

1. 登录成功后，认证 Store 获取当前用户和 `GET /api/v1/user/routes`。
2. 动态路由转换器校验路径、名称、元数据和本地组件映射。
3. 合法路由注册到 `app` 布局，侧边栏根据服务端路由和静态菜单生成。
4. 页面通过 `src/api/<domain>/` 调用后端，响应解析器从 `unknown` 校验为领域类型。
5. 传输层统一处理响应结构、401 刷新、会话版本、错误反馈和文件响应。

### 目录结构

```text
src/
├── api/                    # 领域 API、请求参数和响应解析
├── assets/                 # 全局样式、Lottie 等静态资源
├── components/             # 跨页面公共组件和应用壳层组件
├── hooks/                  # Vue、Router、Pinia、DOM 和第三方实例编排
├── layouts/BasicLayout/    # 侧边栏、头部、标签页、内容区和页脚
├── router/                 # 静态路由、守卫、动态路由和缓存规则
├── stores/modules/         # 认证、标签页、偏好和路由 Loading 状态
├── types/                  # API、路由、Store、传输和组件类型
├── utils/                  # 纯工具、传输边界、运行时守卫和基础设施
├── views/                  # 路由级业务页面
└── __tests__/              # Vitest 单元测试和组件测试
```

## 5. 本地开发

### 环境要求

- Node.js `^22.18.0 || >=24.12.0`
- pnpm
- 可访问的 FastAPI Admin 服务，默认开发地址为 `http://127.0.0.1:3000`

### 启动步骤

```sh
pnpm install
pnpm dev
```

默认访问地址为 `http://127.0.0.1:5173`。`pnpm dev` 会先执行完整静态检查，检查通过后再启动 Vite。

开发环境默认把 `/api` 代理到 `http://127.0.0.1:3000`。需要覆盖本机配置时，从 `.env.example` 创建 `.env.local` 并只填写公开配置。所有 `VITE_*` 变量都会进入浏览器构建产物，禁止写入密码、Token、密钥或内部凭据。

### 环境变量

| 变量                     | 说明                      | 默认示例                |
| ------------------------ | ------------------------- | ----------------------- |
| `VITE_APP_TITLE`         | 应用标题和页脚名称        | `FastAPI Admin`         |
| `VITE_API_BASE_URL`      | 浏览器请求的 API 基础路径 | `/api/v1`               |
| `VITE_API_PROXY_TARGET`  | 开发代理目标              | `http://127.0.0.1:3000` |
| `VITE_API_PROXY_ENABLED` | 是否启用 `/api` 开发代理  | `true`                  |
| `VITE_DEV_HOST`          | 开发服务监听地址          | `127.0.0.1`             |
| `VITE_DEV_PORT`          | 开发服务端口              | `5173`                  |
| `VITE_DEV_OPEN`          | 启动后是否自动打开浏览器  | `false`                 |
| `VITE_PREVIEW_HOST`      | Preview 监听地址          | `127.0.0.1`             |
| `VITE_PREVIEW_PORT`      | Preview 端口              | `4173`                  |
| `VITE_BASE_PATH`         | 部署基础路径              | `/`                     |
| `VITE_SOURCEMAP`         | 是否生成 Source Map       | `false`                 |

项目不使用 `VITE_ROUTE_MODE`。认证后的业务路由始终以后端接口为准。

## 6. API 与会话规范

业务接口统一从 `@/api` 或具体领域 API 模块导入。页面和公共组件不得直接创建 Alova 或 Fetch 请求。

常规响应结构为：

```ts
interface ApiResponse<T> {
  code: number
  error_code?: string | null
  message: string
  data: T
}
```

传输层约定：

- API 基础路径默认为 `/api/v1`。
- 领域响应先按 `unknown` 接收，再由 Parser 完成运行时校验。
- 401 响应使用共享刷新请求重试一次，刷新失败后清理当前会话。
- 普通请求错误通过全局 Message 桥展示；登录和退出使用 Notification。
- 文件下载使用独立 Blob 响应路径，不强制套用 JSON 响应结构。
- 新增接口时必须同步请求类型、响应类型、解析器、页面调用方和针对性测试。

## 7. 路由、权限与缓存

静态路由位于 `src/router/modules/`，主要包括登录、修改密码、组件演示和缺省错误页。登录后的业务路由通过 `GET /api/v1/user/routes` 获取，并注册到 `BasicLayout` 下；系统设置通过顶栏用户菜单在右侧抽屉中打开，不创建页面路由或标签页。

服务端 `component` 只允许映射到本地 `src/views/**/*.vue` 白名单。找不到组件、路径无效或名称冲突的路由会被拒绝，不能根据服务端字符串执行任意动态导入。

权限原则：

- 路由守卫负责登录态和页面访问体验。
- `v-permission`、权限 Hook 和操作按钮负责前端可见性。
- 服务端必须再次校验用户、租户、权限码和数据范围。
- 前端隐藏按钮不构成安全边界。

`meta.noCache === false` 的页面允许 KeepAlive，缓存名称为 `RouteTab_<route-key>`。标签页状态存储在 `sessionStorage`，标签列表和组件缓存分别维护。

## 8. 布局、主题与 Loading

`BasicLayout` 由侧边栏、头部、标签栏、内容区和页脚组成，支持三种滚动模式：

| 模式        | 行为                                       |
| ----------- | ------------------------------------------ |
| `content`   | 头部、标签栏和侧边栏固定，仅内容区内部滚动 |
| `workspace` | 右侧工作区整体滚动                         |
| `sticky`    | 头部和标签栏吸顶，右侧其余区域滚动         |

系统设置统一管理浅色、深色或跟随系统主题、主题色、圆角、字体大小、色弱、灰度、内容宽度、布局可见性、中英文、时区、水印和导航反馈，并持久化到 `localStorage`。

路由 Loading 分为两层：

- `GlobalLoading`：用于初始导航和布局外页面切换，覆盖整个浏览器视口。
- `ContentLoading`：用于 `BasicLayout` 内部导航，覆盖稳定的右侧工作区视口；遮罩尺寸与业务页面内容高度解耦，不会因长页面或空页面拉伸、收缩。
- `RouterLoadingBar`：提供顶部导航进度反馈。

`pageTransition` 控制顶部进度条，`loadingAnimation` 控制 Lottie 遮罩。关闭动画只隐藏视觉反馈，不改变路由状态完成逻辑。

生产构建会生成同源 `version.json`。启用更新检查后，应用定时比较构建 ID，发现新版本时显示刷新提示，由用户确认后执行整页刷新。

## 9. 开发规范

### 模块职责

| 类型        | 目录                                    | 职责                                              |
| ----------- | --------------------------------------- | ------------------------------------------------- |
| 公共 UI     | `src/components/`                       | 展示、交互、Props、Emits、Slots 和局部校验        |
| 页面专属 UI | `src/views/<domain>/<page>/components/` | 单一业务页面的展示与交互编排                      |
| Hook        | `src/hooks/use*.ts`                     | Vue 生命周期、Router、Pinia、DOM 和第三方实例管理 |
| Store       | `src/stores/modules/`                   | 跨页面会话、标签页、偏好和共享状态                |
| Domain API  | `src/api/<domain>/`                     | 后端调用、参数转换和响应解析                      |
| Utility     | `src/utils/`                            | 无生命周期、输入输出明确的纯逻辑和基础设施        |

公共组件通过 Props、Emits、`v-model` 或 Slots 通信，不直接调用领域 API。所有监听器、订阅、观察器、定时器和第三方实例都必须提供清理路径。

详细规范：

- [公共组件约定](./src/components/README.md)
- [Hook 使用规范](./src/hooks/README.md)
- [工具函数规范](./src/utils/README.md)
- [前端工程规则](./.codex/README.md)

## 10. 质量门禁

```sh
pnpm run type-check       # TypeScript 和 Vue 类型检查
pnpm run lint             # ESLint
pnpm run lint:style       # Stylelint
pnpm run format:check     # Prettier
pnpm run test:run         # 完整静态检查和 Vitest
pnpm run build            # 完整静态检查和生产构建
git diff --check          # 差异空白检查
```

定向测试示例：

```sh
pnpm exec vitest run src/__tests__/BasicLayout.spec.ts src/__tests__/Lottie.spec.ts
```

Windows 环境中如果 Vite 或 Vitest 报 `spawn EPERM`，应在允许创建子进程的终端重试，并分别报告静态检查、测试和构建结果。

## 11. 构建与部署

| 命令                         | 模式        | 输出目录            |
| ---------------------------- | ----------- | ------------------- |
| `pnpm run build:development` | development | `dist-development/` |
| `pnpm run build:staging`     | staging     | `dist-staging/`     |
| `pnpm run build`             | production  | `dist/`             |

部署要求：

- Web 服务器必须支持 SPA History 回退，将未知前端路径返回 `index.html`。
- `/api` 应反向代理到 FastAPI 服务，或通过 `VITE_API_BASE_URL` 指向可访问地址。
- `VITE_BASE_PATH` 必须与实际部署子路径一致。
- `version.json` 应使用禁止缓存或短缓存策略，静态哈希资源可使用长期缓存。
- 生产环境默认关闭 Source Map；如需开启，应评估源码暴露风险。

## 12. 安全边界

- 禁止在源码、环境文件、日志、URL、截图和测试夹具中写入密码、Token、验证码、MFA、密钥或生产数据。
- 所有服务端数据均视为不可信输入，必须经过类型和运行时校验。
- 菜单、按钮和路由守卫只改善体验，不能替代后端授权。
- 服务端路由只能解析到本地 View 白名单。
- 用户主动启用“记住登录”时，现有实现会把登录凭据写入 `localStorage`，这是已知安全风险；新功能不得扩大该行为，应在独立安全整改中替换。

## 13. 工程文档

仓库内工程事实和执行规则位于 `.codex/`：

- `AGENTS.md`：前端强制实现规则。
- `PROJECT.md`：当前项目事实、脚本、环境和接口。
- `ARCHITECTURE.md`：模块职责和运行时数据流。
- `BOUNDARY.md`：修改范围、安全边界和禁止事项。
- `WORKFLOW.md`：分析、实现、验证和交付流程。
