# 前端实现规则

以下规则适用于 `frontend/` 下的 Vue 应用。规则约束实现方式，不替代当前源码、后端 DTO、Controller、测试和构建配置对接口事实的证明。

## 范围和优先级

- 前端改动默认只位于 `frontend/`，不得修改 `service/`、部署文件、数据库迁移、`node_modules/`、`dist/`、覆盖率目录、缓存或锁文件。
- 需求、当前源码和后端契约优先于本目录规则；发现规则与代码冲突时，先核实真实行为，再更新规则或请求契约决策。
- 使用 Vue 3、Composition API、`<script setup lang="ts">`、TypeScript strict、Pinia、Vue Router、Alova 和 Naive UI。未经过明确决策，不新增同类框架或 HTTP 客户端。
- 新增或修改的中文规则、注释、文档和任务模板使用中文；命令、路径、API 字段和标准技术名称保留原文。

## 类型规则

- 所有共享类型必须定义在 `src/types/` 的独立类型文件中，禁止在页面、组件、API、路由和 Store 文件中定义可跨模块使用的 `interface`、`type` 或枚举。
- 按领域拆分类型，例如 `src/types/api/auth.ts`、`src/types/api/user.ts`、`src/types/router.ts`、`src/types/store.ts`；每个领域目录通过 `index.ts` 汇总，`src/types/index.ts` 提供根统一出口。
- API 类型保留后端蛇形字段，例如 `access_token`、`refresh_token`、`tenant_id` 和 `must_change_password`。只有明确的 UI 适配器可以转换为前端展示字段。
- 类型文件只声明类型、常量类型和纯运行时守卫，不发起请求、不执行路由跳转、不读取 Store、不访问 DOM。
- 运行时解析器与类型声明分离：API 响应解析放在对应 API 模块的 `parsers.ts` 或 `src/utils/guards/`，不得继续把所有领域类型和解析器堆在单一文件中。
- 禁止使用 `any`、`@ts-ignore`、无检查的类型断言和通过放宽类型掩盖接口不一致。

## 图标规则

- UI 图标统一使用 Ionicons 5：图标从 `@vicons/ionicons5` 导入，禁止混用其他图标集、手写 SVG、Emoji、Unicode 字符或 CSS 绘制图标作为功能图标。
- 需要统一尺寸、颜色或 `aria-hidden` 行为时，使用 `Icon` 包装器；包装器来源为 `@vicons/utils`。当前仓库尚未声明该包装器依赖，使用前必须先完成依赖声明和锁文件变更，不能隐式依赖传递安装。
- 图标按钮必须提供 `aria-label` 和 `title`（当图标含义不明显时），文本按钮只用于明确的文字命令；不要用带文字的圆角矩形替代已有的常见图标命令。
- 菜单图标、头部操作图标、主题/全屏/返回/刷新/删除/编辑图标都必须遵守同一图标集和尺寸规范。业务图标由页面或领域模块传入，不在通用按钮中猜测。

## 模块和统一出口

新代码按领域模块组织，禁止继续扩大单文件聚合结构：

```text
src/
├── api/
│   ├── auth/
│   │   ├── index.ts
│   │   └── parsers.ts
│   ├── user/
│   │   ├── index.ts
│   │   └── parsers.ts
│   └── index.ts
├── router/
│   ├── modules/
│   │   ├── public.ts
│   │   ├── system.ts
│   │   └── index.ts
│   ├── guards/
│   │   ├── auth.ts
│   │   └── index.ts
│   └── index.ts
├── stores/
│   ├── modules/
│   │   ├── auth.ts
│   │   ├── app.ts
│   │   └── index.ts
│   └── index.ts
└── types/
    ├── api/
    │   ├── auth.ts
    │   ├── user.ts
    │   └── index.ts
    ├── router.ts
    └── index.ts
```

- 每个领域目录必须有自己的 `index.ts`，根目录必须有统一出口；业务调用方优先从 `@/api`、`@/router`、`@/stores`、`@/types` 导入，不得跨模块引用实现文件。
- 统一出口只负责导出，不放业务逻辑、请求、Store 实例化、路由守卫或副作用；禁止形成循环依赖。
- `export *` 只允许用于无冲突的领域出口；同名导出必须使用显式命名导出，避免统一出口覆盖字段或函数。
- 迁移旧单文件时保持兼容导出，完成调用方迁移和测试后再删除旧入口；不得为了目录改造改变 API 路径、路由名称、权限码或 Store 行为。

## 页面和分层

- 页面只负责展示、交互和页面级编排；业务规则放在 Store、composable 或 service API 层。
- 请求只能通过 `src/api/<domain>/index.ts` 进入传输层，页面和 Store 不得直接调用 Alova、拼接 URL、设置 Authorization 或解析统一响应。
- 路由模块只声明路由；认证守卫、动态路由校验和注册分别放在 `router/guards` 与 `router` 的专属模块中。
- Store 只管理跨页面状态和动作，不访问 DOM，不直接依赖页面组件，不保存服务端密钥。
- 组件必须明确加载、成功、空数据、校验失败、401、403、限流、网络错误、取消和可重试状态。

## 安全和质量

- 后端是认证、授权、租户、数据范围、业务状态和数据一致性的最终权威。前端隐藏按钮或路由不能替代后端权限校验。
- Token、密码、MFA、图形验证码、密码重置令牌和真实生产数据不得写入日志、URL、源码、截图或长期浏览器存储。
- 禁止 `v-html`、任意动态组件、未经校验的外链/iframe、任意 `window.open` 和把服务端组件路径直接作为动态导入地址。
- 修改完成后至少执行 `pnpm run type-check`、`pnpm run lint`、`pnpm run lint:style`、`pnpm run format:check`、相关单元测试和 `git diff --check`。
