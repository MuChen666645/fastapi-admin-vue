# 前端开发规则

本文件是 `frontend/` 的规则入口。修改前端文件前，先读取仓库根目录 `AGENTS.md`，再按 `frontend/.codex/README.md` 的顺序阅读前端核心文档。

## 适用范围与优先级

- 本目录只维护 Vue 前端。默认不修改 `service/`、部署文件、数据库迁移、`node_modules/`、`dist*/`、缓存、覆盖率目录、临时构建目录或锁文件。
- 规则文档不能代替源码、测试、配置和后端契约。发生冲突时，先以当前源码和测试核实，再更新文档或提出契约决策。
- 用户本轮要求优先于本文件；后端认证、授权、租户、数据范围和业务状态始终是最终权威。
- 新增或修改的中文规则、注释和文档使用中文；命令、路径、接口字段和技术名称保留原文。

## 当前技术栈

- Vue 3、`<script setup lang="ts">`、TypeScript strict、Vite、Vue Router、Pinia、Alova、Naive UI、UnoCSS。
- 包管理器为 pnpm，Node 版本以 `package.json` 的 `engines` 为准。
- 路径别名 `@` 指向 `src/`；图标统一使用 `@vicons/ionicons5`。
- 业务菜单统一从后端 `GET /api/v1/user/routes` 获取；项目不再使用 `VITE_ROUTE_MODE`，仅保留不显示菜单、用于字典类型页跳转的静态 `system-dict-data` 路由。

## 分层约束

### API 与传输

- 页面和 Store 只能从 `@/api` 调用领域 API，不得直接使用 Alova、`fetch`、Axios、拼接 URL 或设置 Authorization。
- `src/api/<domain>/index.ts` 只负责请求契约，响应解析放在同领域 `parsers.ts`；统一传输、响应包装、401 刷新和错误归一化由 `src/utils/request.ts` 处理。
- 后端蛇形字段在 API 类型中原样保留。只有明确命名的适配器才能转换为 UI 字段。
- 不新增假接口、猜测字段、猜测枚举、静默 Mock 或客户端权限替代。

### 路由

- 静态路由位于 `src/router/modules/`，当前分为 `public.ts`、`protected.ts`、`error.ts`。
- `protected.ts` 提供登录后的 `app` 布局、修改密码页、`system-settings` 系统设置入口和隐藏的 `system-dict-data` 字典数据页；后端业务路由由 `registerAuthenticatedRoutes()` 添加到 `app` 下。
- 动态路由的 `component` 只能经过 `src/router/route-utils.ts` 的本地 `import.meta.glob('../views/**/*.vue')` 白名单解析。路径不安全或组件不存在时过滤该路由并输出一次警告。
- 路由守卫位于 `src/router/guards/auth.ts`，只负责会话初始化、密码变更重定向、动态路由注册和安全导航，不实现业务授权。

### Store 与页面

- Pinia Store 位于 `src/stores/modules/`，分别管理会话、标签页和路由 Loading 状态；Store 不访问 DOM、不依赖页面组件、不保存服务端密钥。
- 页面负责展示、交互和页面级编排。跨页面状态放 Store，可复用行为放 `src/hooks/` 或 `src/utils/`，领域请求放 API 层。
- 系统设置页面的业务面板放在 `src/views/system/config/components/`，父页面只负责标签切换和统一重置。

### Loading 与缓存

- `GlobalLoading` 和 `ContentLoading` 共用 `useRouteLoadingStore` 与 `car-loading3-data.json`。
- 离开或进入 `app` 布局的导航使用全屏 Loading；`app` 布局内的页面切换使用内容区 Loading；已缓存的路由切换不重复显示 Loading。
- `BasicLayout` 在内容区内使用 `KeepAlive`。`meta.noCache === false` 表示允许缓存，组件缓存名由 `RouteTab_<route-key>` 生成；标签页状态单独由 `useTabsStore` 持久化。

## 类型、图标与安全

- 所有 production 和 test 中的 `type`、`interface`、`enum` 声明都必须放在 `src/types/` 的语义化领域文件中，并通过 `@/types` 统一出口导出；页面目录、组件目录、Hook、Store、Router 和工具文件不得内联声明类型。
- 新增或修改 CSS 时优先使用 UnoCSS utility class；仅在组件专属复杂选择器、伪元素、关键帧、CSS 变量或第三方覆盖等 utility 不适合表达的场景使用 `<style lang="scss" scoped>`。
- `src/views/` 下的目录必须使用能表达业务域或页面职责的语义化名称，采用现有的小写 kebab-case 约定；禁止使用 `page`、`view`、`temp`、`common`、`misc`、数字或无意义缩写。页面私有业务组件放在对应页面的 `components/`，公共组件放在 `src/components/`。
- 禁止 `any`、`@ts-ignore`、无检查的类型断言和用放宽类型掩盖接口不一致。
- 功能图标必须静态导入 Ionicons 5；禁止混用图标库、手写 SVG、Emoji、Unicode 字符或 CSS 图形表达功能。
- 图标按钮提供 `aria-label`，含义不明显时同时提供 `title`；装饰图标使用 `aria-hidden="true"`。
- 禁止 `v-html`、`innerHTML`、任意 iframe、未经校验的外链、任意 `window.open` 和把服务端组件路径直接传给 `import()`。
- Token、密码、验证码、MFA、密码重置令牌和生产数据不得写入日志、URL、源码、截图或测试输出。当前登录偏好仍会在用户主动选择记住登录时写入浏览器存储，修改此行为必须单独进行安全评审。

## 验证要求

修改完成后至少执行：

```text
pnpm run check
pnpm run test:run
pnpm run build
git diff --check
```

其中 `pnpm run check` 包含 TypeScript、ESLint、Stylelint 和 Prettier 检查。Windows 下若 Vite/Vitest 遇到 `spawn EPERM`，应在允许子进程的环境重试，并分别报告静态检查和运行时验证结果。
