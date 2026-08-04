# 前端工作流

本流程适用于 `frontend/` 的功能开发、缺陷修复、路由/接口变更、重构和规则文档维护。

## 1. 识别任务范围

先判断任务属于：

- 功能开发：新增页面、交互、路由或 API 接入。
- 缺陷修复：已有路径的行为不符合预期。
- 契约变更：接口方法、路径、字段、响应或权限改变。
- 重构：只改善模块边界和可维护性，保持行为兼容。
- 规则/文档维护：只更新文档事实、流程和模板。

明确本轮是否允许修改后端。默认前端任务只修改 `frontend/`；需要接口事实时可以只读核对后端 Controller、DTO、配置和测试。

## 2. 修改前检查

1. 阅读仓库根目录 `AGENTS.md`、`frontend/AGENTS.md` 和 `.codex/` 核心文件。
2. 执行 `git status --short`，识别用户已有修改，不回滚、不覆盖、不顺手格式化无关文件。
3. 使用 `rg` 查找目标路由、组件、Store、API、类型、环境变量和测试。
4. 阅读 `package.json`、`env.d.ts`、`vite.config.ts`、`vitest.config.ts`，确认实际脚本和构建行为。
5. 如果涉及接口，核对请求方法、相对路径、编码、响应包装、错误、登录态和权限；不根据 README 猜接口。
6. 如果涉及路由，核对静态模块、守卫、动态注册、组件解析、菜单、标签页和 KeepAlive 的调用链。
7. 如果涉及 Loading，核对 `route-loading` Store、GlobalLoading、ContentLoading、RouterLoadingBar 和布局边界。

## 3. 设计与实现顺序

### 接口和类型任务

1. 在 `src/types/` 定义请求、响应或状态类型。
2. 在 `src/api/<domain>/index.ts` 增加接口函数，在 `parsers.ts` 增加 `unknown` 运行时解析。
3. 从 `src/api/index.ts` 和 `src/types/index.ts` 提供显式统一出口。
4. 在 Store 或 hook 中编排加载、取消、错误、重试和状态转换。
5. 页面只消费已验证数据，不复制请求和解析逻辑。

### 路由任务

1. 明确路由是公开、认证静态、认证动态还是错误路由。
2. 静态声明放 `src/router/modules/`；认证逻辑放 `src/router/guards/`。
3. 后端动态路由必须经过 API parser 和 `route-utils.ts` 本地 View 白名单。
4. 覆盖未找到组件、危险路径、重复路由、空容器、外链和刷新动态路由场景。

### 页面和组件任务

1. 先复用现有 Naive UI、布局组件、hooks 和 Store。
2. 页面只负责展示、交互和页面级编排；跨页面状态放 Store，可复用行为放 hook。
3. 页面内多个业务区域放在该页面的 `components/`，通过明确的 props/emits 连接；类型声明统一放入 `src/types/`，不在页面组件或 `components/` 下创建 `types.ts`。
4. 补齐加载、空数据、错误、无权限、禁用、重复提交和取消状态。
5. 功能图标静态导入 `@vicons/ionicons5`，按钮补充可访问名称。
6. 新增可复用组件或组件组时，同步编写所属目录 `README.md`，并提供 Props、Emits、Slots、暴露方法、状态边界和最小使用示例；需要演示时接入静态演示路由。

### 工具函数和 Hooks 任务

1. 先判断实现是否需要 Vue 生命周期、Router、Pinia、DOM Ref 或组件上下文；不需要时放入 `src/utils/`，需要时放入 `src/hooks/`。
2. 工具函数保持输入、输出和失败行为明确；公共工具从 `@/utils` 导出，基础设施工具保留具体入口，并为外部输入、存储不可用和安全校验补边界测试。
3. Hook 使用 `use` 命名，只编排可复用行为，不直接请求领域 API；所有监听器、订阅、观察器、定时器和第三方实例都必须有清理路径。
4. 跨页面状态放 Pinia Store，不通过模块级可变变量或 Hook 私有缓存共享业务数据；敏感数据不得进入 Store、Hook、工具持久化或复制功能。
5. 修改工具或 Hook 时同步更新 `src/utils/README.md`、`src/hooks/README.md`、公共出口和相关测试；删除或迁移时清理旧入口和旧文档。

### 文档任务

1. 先从源码、配置和测试中确认事实。
2. 将事实写入 `PROJECT.md`，将依赖方向写入 `ARCHITECTURE.md`，将安全与范围写入 `BOUNDARY.md`。
3. 将可重复执行的步骤写入本文件，将规则写入 `AGENTS.md`，将任务输入模板写入 `PROMPTS/`。
4. 检查 README、规则和模板是否仍包含旧路径、旧脚本、旧环境变量或第二套约定。

涉及偏好配置或双语模式时，额外核对：

1. 所有开关是否连接到 `usePreferencesStore`，是否有默认值、持久化和恢复默认行为。
2. 语言切换是否只影响前端界面文案；未知动态标题、后端字段和权限契约是否保持原样。
3. 内容区 `content`、`workspace`、`sticky` 三种滚动模式是否分别覆盖内部滚动、右侧整体滚动和顶部 sticky 行为。
4. 文档是否同时更新中文 README、`README.en.md` 以及 `.codex/` 中的项目事实、架构和边界说明。

## 4. 测试设计

按风险添加针对性测试：

- API parser：缺字段、错误类型、默认值和不可信结构。
- 认证 Store：密码变更状态、刷新令牌、初始化去重、失败重试和退出清理。
- 动态路由：路径/名称安全、组件解析、缺失组件警告、容器重定向和重复注册。
- 路由缓存：可缓存/不可缓存页面、标签页刷新、关闭标签和 KeepAlive 名称隔离。
- Loading：初始全屏、布局内内容区、布局外全屏、缓存路由跳过、导航错误和动画销毁。
- 公共组件：Props/Emits/v-model、插槽、暴露方法、校验、Loading、防重复提交和卸载清理。
- Hooks：初始化、响应式更新、Router/Store 联动、无 DOM 或无 Pinia 降级和生命周期清理。
- 工具函数：正常输入、边界输入、错误类型、空值、外部响应、存储失败和安全拒绝路径。
- 页面：关键可见内容、交互切换、错误提示和没有后端数据时的安全状态。

不要为了让测试通过而放宽类型、权限、解析规则或异常处理。

## 5. 验证命令

在 `frontend/` 目录执行：

```text
pnpm run check
pnpm run test:run
pnpm run build
git diff --check
git status --short
```

按需补充：

```text
pnpm exec vitest run src/__tests__/DynamicRouter.spec.ts
pnpm exec vitest run src/__tests__/Lottie.spec.ts
pnpm exec vitest run src/__tests__/SystemConfig.spec.ts
pnpm exec prettier --check "*.md" ".codex/**/*.md"
```

`pnpm run build` 会再次执行 `check`。Windows 下若 Vitest/Vite 报 `spawn EPERM`，先保留已通过的静态检查，再在允许子进程的环境重试运行时命令，报告两者结果，不用“应该可以”替代验证。

## 6. 交付前审查

- 只修改用户要求范围，保留无关工作区变化。
- 检查没有死代码、死导出、旧环境变量、旧路径、重复出口或循环依赖。
- 检查敏感数据没有进入源码、日志、URL、截图和测试输出。
- 检查动态路由仍只解析本地组件，后端权限仍由服务端执行。
- 检查组件、Hook 和工具的 README、公共出口、类型和测试与当前源码一致。
- 说明构建警告、未执行验证和已知风险，不把 warning 写成成功。

## 7. 中文交付模板

```text
完成结果：
修改文件：
当前事实和设计决策：
接口、路由、Store 和缓存影响：
安全与权限边界：
验证命令及结果：
未完成验证及原因：
剩余风险：
```
