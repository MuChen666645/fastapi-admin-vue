---
name: fullstack-validation
description: 为本仓库的前后端联动变更选择并执行分层验证，包括前端静态检查与 Vitest、后端 pytest 与编译、Alembic 离线 SQL、构建、Docker/MySQL/Redis/浏览器联调，以及验证边界报告时使用。
---

# 全栈验证

用于把两端验证结果拆开报告。单端测试通过不等于 HTTP 契约、数据库、Redis、Docker、浏览器或
第三方服务已经验证。

## 工作流程

1. 根据改动分类：前端 API/页面/路由/布局、后端 DTO/Controller/Service/DAO、认证权限租户、
   迁移/seed、调度/Worker、构建或部署。
2. 先运行最小相关验证，再扩展共享边界测试。前端使用 Vitest 和 `pnpm run check`；后端使用
   pytest、compileall 和必要的离线 Alembic SQL。
3. 影响前端构建、公共资源、Vite 或发布配置时运行 `pnpm run build`。影响 schema 时运行
   `poetry run alembic upgrade head --sql`，真实数据库升级另行记录。
4. 仅在环境、目标、凭据来源和数据影响已确认后运行 Docker、MySQL、Redis、浏览器、OIDC、
   LDAP、SMTP、OSS 或生产验证。
5. 失败时从第一条错误定位根因，不通过跳过测试、放宽类型、权限或校验掩盖问题。
6. 输出通过、失败、未执行和未覆盖四类结果，并说明每类覆盖的实际行为。

详细选择规则见 [validation-matrix.md](references/validation-matrix.md)。
