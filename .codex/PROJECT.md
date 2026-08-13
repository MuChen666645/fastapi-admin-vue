# 仓库项目事实

## 项目组成

| 目录 | 技术栈 | 主要责任 |
| --- | --- | --- |
| `frontend/` | Vue 3、TypeScript、Vite、Pinia、Alova、Naive UI、UnoCSS | 管理端页面、交互、会话体验和类型化 API 调用 |
| `service/` | FastAPI、SQLModel、MySQL、Redis、Alembic、Poetry | 认证、授权、租户、业务规则、持久化和后台任务 |

两端通过 HTTP 协作，不共享运行时模块。跨端行为以 service 当前 Controller、DTO、测试和前端实际调用共同核验。

## 目录入口

| 主题 | 前端 | 后端 |
| --- | --- | --- |
| 规则 | `frontend/AGENTS.md`、`frontend/.codex/` | `service/AGENTS.md`、`service/.codex/` |
| Skill | `frontend/.agents/skills/` | `service/.agents/skills/` |
| API/HTTP | `src/api/`、`src/utils/request.ts` | `module_admin/controller/`、`module_admin/v1.py`、拦截器 |
| 身份权限 | `src/stores/modules/auth.ts`、`src/router/guards/` | `module_admin/auth/`、权限与租户 Service |
| 测试 | `src/__tests__/`、Vitest | `test/`、pytest |

## 已核验契约基线

- 管理 API 使用后端 `settings.API_V1_PREFIX`，当前为 `/api/v1`。
- 后端统一响应拦截器处理通常的 JSON 响应；文件、流和原始响应按现有跳过包装规则处理。
- 前端 `request.ts` 负责传输、认证、响应包装、刷新和错误归一化；API Parser 校验 `unknown` 数据。
- 登录后前端从 `/api/v1/user/routes` 加载并白名单解析服务端动态路由。
- 后端当前 Alembic head 为 `0028_tenant_and_system_parameter_menus`；已应用迁移源码属于部署历史，不得删除或重写。
- 前端验证以 `pnpm run check`、`pnpm run test:run`、必要时 `pnpm run build` 为主；后端验证以 pytest、compileall 和离线迁移 SQL 为主。

## 运行依赖

前端开发使用 `frontend/package.json` 规定的 Node/pnpm；后端使用 Poetry 和 Python 3.11。MySQL、Redis、Docker、
浏览器、OIDC/LDAP/SMTP、OSS 等外部依赖是否可用，必须在验证结果中单独说明。
