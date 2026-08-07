# 前端 Codex 核心规则

本文件是 `frontend/.codex/` 的强制实现规则。它约束代码组织、安全边界和验证方式，不替代当前源码、测试、构建配置或后端接口契约。

## 规则加载

修改前端文件前按以下顺序读取：

1. 仓库根目录 `AGENTS.md`。
2. `frontend/AGENTS.md`。
3. 本文件。
4. `PROJECT.md`、`ARCHITECTURE.md`、`BOUNDARY.md`、`WORKFLOW.md`。
5. 与任务对应的 `PROMPTS/feature.md` 或 `PROMPTS/bugfix.md`。

## 必须遵守

- 使用 Vue 3 Composition API、`<script setup lang="ts">`、TypeScript strict、Pinia、Vue Router、Alova 和 Naive UI；不在未评审时引入同类框架或 HTTP 客户端。
- 所有请求经过 `src/api/<domain>/index.ts` 和 `src/utils/request.ts`。页面和 Store 不得直接访问 Alova、`fetch`、Axios 或服务端 URL。
- API 响应先由 `parsers.ts` 接收 `unknown` 并校验，再交给业务层；禁止用类型断言绕过校验。
- 所有 production 和 test 中的 `type`、`interface`、`enum` 声明都放在 `src/types/` 的语义化领域文件中，并通过 `@/types` 统一出口导出；页面、组件、Hook、Store、Router 和工具文件只允许导入类型，不允许声明类型。
- 编写样式时优先使用 UnoCSS utility class。`<style scoped>` 仅用于组件专属复杂选择器、伪元素、关键帧、CSS 变量和第三方样式覆盖；不要为普通布局、间距、颜色和响应式规则新增重复 CSS。
- `src/views/` 下的目录名必须语义化并描述业务域或页面职责，使用现有的小写 kebab-case 约定；禁止 `page`、`view`、`temp`、`common`、`misc`、数字和无意义缩写。页面业务组件放到对应页面的 `components/`，跨页面复用组件放到 `src/components/`。
- 路由模块只声明路由，守卫只处理认证和安全重定向，动态路由只从本地 View 白名单解析。
- Store 只管理跨页面状态和动作，不访问 DOM、不依赖页面组件、不保存服务端密钥。
- 功能图标统一从 `@vicons/ionicons5` 静态导入；按钮必须有可访问名称，装饰图标必须 `aria-hidden`。
- 不写入真实密钥、Token、密码、验证码、MFA、生产数据、临时日志或生成物。
- 不用假数据、静默 Mock、`any`、`@ts-ignore`、无检查断言或放宽权限来掩盖问题。
- 可复用组件或组件组必须在所属目录维护 `README.md`；文档至少说明用途边界、Props、Emits、Slots、暴露方法、校验/状态约定和最小使用示例，并与源码和测试同步更新。
- 组件文档中的提交示例必须通过页面的 `@submit` 调用 `@/api`，组件本身只负责展示、交互和校验，不得把业务请求写入通用组件。

## 组件、工具函数和 Hooks 规范

### 组件

- 跨页面复用的组件放在 `src/components/<ComponentName>/`，页面专属组件放在对应页面的 `src/views/<domain>/<page>/components/`；不能因为暂时只有一个调用方就把业务组件提升为全局组件。
- 组件只负责展示、用户交互、局部状态和局部校验。组件不直接调用 `@/api`、Alova、`fetch` 或 Axios，不读取业务接口原始响应，不保存 Token、密码、业务列表和跨页面业务状态。
- 通用组件通过 Props 接收数据和配置，通过 Emits 或 `v-model` 交付变化；提交表单时先完成组件内校验，再由页面或领域 Store 调用已核实的 `@/api`。
- 组件公开的 Props、Emits、Slots、`defineExpose` 方法和校验/Loading 状态必须有稳定类型，并在所属目录 README 中记录；类型声明统一从 `@/types` 导入。
- 应用壳层组件可以使用明确指定的 Router、Pinia Store 或基础工具（例如路由 Loading、Message 桥和水印），但必须只挂载一个实例，并在卸载时清理监听器、回调、观察器和动画实例。
- 组件测试放在 `src/__tests__/`，优先验证公开渲染、事件、校验、Loading、防重复提交和卸载清理行为；不要为了测试内部变量而暴露额外 API。

### 工具函数

- 无 Vue 生命周期、Router、Pinia 或组件上下文依赖的纯计算、格式化、解析、转换和存储逻辑放在 `src/utils/`，公共工具通过 `src/utils/index.ts` 和 `@/utils` 导出。
- 工具函数应保持输入、输出和失败行为明确；处理 `unknown`、外部响应、路由、外链和浏览器存储时必须先校验，不能用 `any`、无检查断言或静默成功掩盖异常。
- `request.ts`、`request-feedback.ts`、`guards/api.ts`、`guards/route.ts` 属于工具目录中的基础设施边界，必须保留各自职责；页面和 Store 不得因此直接绕过 `@/api` 调用传输层。
- 工具函数不得创建隐式全局可变状态、修改业务 Store 或依赖组件生命周期。需要生命周期、Router 或 Pinia 上下文时，应改为 Hook 或 Store。
- 浏览器存储工具必须安全处理 SSR、不可用存储和解析失败，不得新增或扩大敏感数据持久化；Lottie 基础函数只管理实例动作，生命周期销毁由 `useLottie` 或所属组件负责。
- 新增公共工具必须补充 `src/utils/README.md`、`src/utils/index.ts`（基础设施例外需说明具体入口）和针对边界行为的单元测试。

### Hooks

- 依赖 Vue 生命周期、Router、Pinia、DOM Ref 或组件上下文的可复用行为放在 `src/hooks/use*.ts`，统一使用 `use` 命名；项目不新增第二套 `composables` 目录。
- Hook 只封装可复用的交互和生命周期编排，不直接调用领域 API、不提交业务表单、不解析后端响应；领域请求由页面、Store 或 API 层负责。
- Hook 可以读取或更新明确的 Pinia UI 状态，也可以使用 Router，但不得通过模块级可变变量共享跨页面业务状态，不得把 Token、密码或业务数据写入 Hook 私有缓存。
- Hook 创建的监听器、订阅、ResizeObserver、Router 回调、定时器和第三方实例必须在卸载或停止时清理；重复调用不能产生重复监听或泄漏。
- 返回值应优先使用响应式 Ref、Computed 或明确动作函数，调用方只依赖公开返回合同；Hook 中的类型从 `@/types` 导入，不在文件内声明领域类型。
- 新增或修改 Hook 必须同步 `src/hooks/README.md` 和 `src/hooks/index.ts`，并用组件测试或单元测试覆盖初始化、更新、清理和无 DOM/无 Pinia 的安全降级行为。

## 当前路由事实

- `src/router/index.ts` 创建 Router、注册静态路由和认证守卫，并暴露动态路由注册/清理能力。
- `src/router/modules/public.ts` 提供双语登录页，`protected.ts` 提供认证入口、修改密码页、`system-settings` 和“演示 / 功能 / 表单、搜索表单、Hooks、工具函数、缺省页 / 403、404、500、网络离线”静态菜单树，`error.ts` 提供 403、404、500 和离线页面。
- 认证后通过 `GET /api/v1/user/routes` 获取业务路由，并将通过校验的路由添加到 `app` 布局下。
- 项目不再使用 `VITE_ROUTE_MODE`，不再维护前端静态业务路由清单。

## 当前状态事实

- `auth` Store 管理 Token、当前用户、权限、后端路由和初始化状态；仅持久化刷新 Token 与记住的用户名。
- `tabs` Store 使用 `sessionStorage` 持久化标签页；`route-loading` Store 管理 `screen`/`content` 两种 Loading 范围，并保持最短可见时间。
- `BasicLayout` 将内容区 Loading、标签页、面包屑、KeepAlive 和路由页面组合在一起。
- Lottie 封装位于 `src/utils/lottie.ts` 和 `src/hooks/useLottie.ts`，动画组件使用 `src/assets/lottie/car-loading3-data.json`。

## 页面文件规模

- `src/views/**/*.vue` 页面文件的源代码行数上限为 600 行，统计范围包括 `<script>`、`<template>`、`<style>`、注释和空行；`dist/`、缓存和其他生成文件不计入。
- 新建或修改页面时，若文件超过 600 行，必须在同一任务中完成原因分析和拆分，禁止通过删除空行、压缩代码、合并不相关职责或关闭检查规避限制。
- 页面文件只保留路由入口、页面级状态编排、查询/分页协调、权限分支和领域 API 调度；列表、表单、详情、弹窗、复杂表格列和重复交互应拆到当前页面的 `components/`，无生命周期的解析/格式化逻辑放到 `src/utils/`，跨页面组件才提升到 `src/components/`。
- 业务组件拆分后必须保持原有路由、API 契约、权限控制、校验、Loading、错误反馈和提交行为；组件通过 Props、Emits 或 `v-model` 与页面交互，不得把领域 API 写入通用或展示组件。
- 存量超限页面要在后续修改该业务时优先完成拆分和代码优化；本次未涉及的存量超限页面必须在交付说明中明确记录，不得把超限作为长期例外。

## 维护规则

当确认了 API、路由、权限、依赖、目录职责、缓存或构建脚本变化时，必须同步更新 `PROJECT.md`、`ARCHITECTURE.md`、`BOUNDARY.md` 或 `WORKFLOW.md` 中受影响的事实。文档不得保留已经删除的路径、变量、脚本或兼容分支。

新增可复用组件时，必须同时检查组件目录的 `README.md`、`src/types/` 类型出口、组件级测试和必要的静态演示路由；仅新增源码而没有使用文档或验证用例不视为完整交付。
