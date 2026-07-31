# 前端功能开发模板

维护目录：`E:/fastapi-admin-vue/frontend`

开始前阅读：仓库根目录 `AGENTS.md`、`frontend/AGENTS.md`、`.codex/AGENTS.md`、`.codex/PROJECT.md`、`.codex/ARCHITECTURE.md`、`.codex/BOUNDARY.md` 和 `.codex/WORKFLOW.md`。

## 需求输入

```text
功能名称：
业务目标：
目标路由或页面：
用户角色和权限：
涉及接口：
成功标准：
异常和空状态：
```

## 开发要求

1. 先检查现有页面、组件、路由、Store、API、类型、环境配置和同类测试，确认能否复用。
2. 涉及接口时核对真实方法、完整路径、请求编码、响应包装、错误结构、登录态、权限和字段命名；后端默认只读核对，不修改后端。
3. 先设计数据流：页面/组件 -> hook 或 Store -> `@/api` -> `src/utils/request.ts` -> FastAPI。
4. 所有 `type`、`interface`、`enum` 声明放入 `src/types/` 并通过 `@/types` 导入；响应解析放入 API 领域的 `parsers.ts`。新增 CSS 优先使用 UnoCSS，`views` 下目录使用语义化名称；禁止 `any`、未经检查的断言和猜测字段。
5. 静态路由放 `src/router/modules/`，后端动态路由必须通过本地 View 白名单解析；项目不使用 `VITE_ROUTE_MODE`。
6. 页面只负责展示、交互和编排。页面较大时，将业务面板拆到该页面的 `components/`，不要复制成全局公共组件。
7. 跨页面状态进入 Pinia Store，可复用生命周期和局部行为进入 `src/hooks/`；Store 不访问 DOM、不依赖页面组件。
8. 功能图标从 `@vicons/ionicons5` 静态导入，图标按钮补充 `aria-label`/`title`，装饰图标使用 `aria-hidden`。
9. 覆盖加载、成功、空数据、校验失败、401、403、网络错误、取消、重复提交和可重试状态；不要使用假数据掩盖真实错误。
10. 涉及缓存或 Loading 时，分别验证 tabs 持久化、KeepAlive 缓存、路由刷新、全屏 Loading 和内容区 Loading。

## 验收和验证

```text
验收路径：
关键断言：
异常路径：
权限边界：
```

在 `frontend/` 目录执行：

```text
pnpm run check
pnpm run test:run
pnpm run build
git diff --check
```

## 交付报告

```text
实现内容：
接口和数据契约：
路由、Store、缓存和 Loading 影响：
权限和安全处理：
验证结果：
未完成验证及原因：
涉及文件：
剩余风险：
```
