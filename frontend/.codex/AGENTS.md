# 前端工程规则

## 技术栈

- 使用 Vue 3 Composition API、`<script setup lang="ts">`、TypeScript、Vue
  Router、Pinia、Alova、Naive UI 和 UnoCSS。
- 默认使用 `const`；非重载函数默认使用箭头函数。
- 领域类型统一位于 `src/types/`，通过 `@/types` 导入。不得在页面、组件、
  Store、路由、Hook、工具或测试中内联声明领域类型。

## 分层

```text
页面或布局 -> Store 或页面编排 -> @/api -> 请求传输层
```

- 页面负责展示、路由状态、权限和领域动作编排。
- 可复用 UI 通过类型化 Props 接收数据、通过事件交付用户意图；不得调用 API
  或持有跨页面业务状态。
- Store 管理跨页面状态和动作；不得访问 DOM。
- API 模块调用 `requestJson`，Parser 校验 `unknown` 响应后再返回类型化数据。
  页面、组件、Hook 和 Store 不得直接调用 Alova、`fetch`、Axios 或后端 URL。
- 依赖生命周期、Router 或 Pinia 的复用逻辑放在 `src/hooks/`；纯转换和校验
  放在 `src/utils/`。

## 路由与权限

- 静态路由位于 `src/router/modules/`；守卫负责认证、安全重定向和静态路由权限。
- 服务端动态路由只能通过 `route-utils.ts` 的本地视图白名单解析。路由记录、
  链接和查询参数均视为不可信输入。
- 每个业务操作必须绑定已核验的权限码。可见性和 handler 使用同一判定；前端
  仅改善体验，后端仍是最终授权边界。

## UI 与安全

- 优先使用 UnoCSS utility；仅在复杂组件选择器、伪元素、关键帧、CSS 变量或
  第三方样式覆盖时使用 scoped CSS。
- 功能图标使用静态导入的 `@vicons/ionicons5`，图标按钮必须有可访问名称。
- 禁止 `any`、`@ts-ignore`、未校验类型断言、`v-html`、原始 `innerHTML`、
  任意 iframe、不安全外链、生产 Mock 数据和猜测的 API 契约。
- 不得持久化或记录 Token、密码、验证码、MFA、重置令牌或敏感服务端数据。新增
  浏览器持久化属于安全变更。

## 测试与文档

- 为行为、契约、校验、权限、Loading 和错误路径增加或更新聚焦测试；避免只断言
  静态文案、实现细节或演示页面结构的低价值测试。
- 页面不超过 600 行；将表单、表格、弹窗和复杂交互拆到路由局部 `components/`。
- 仅当已核验事实变化时更新 `.codex`；组件、Hook 或工具的公开契约变化时同步
  更新对应 README。
