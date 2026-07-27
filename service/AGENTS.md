# 后端 Codex 入口

修改 service/ 下的文件前，必须按以下顺序阅读项目规则：

1. 仓库根目录 AGENTS.md：全局范围、安全和协作规则。
2. .codex/PROJECT.md：项目事实、目录职责和 API 约定。
3. .codex/ARCHITECTURE.md：应用生命周期、分层、会话和后台任务架构。
4. .codex/BOUNDARY.md：权限、租户、数据库、外部系统和禁止事项。
5. .codex/WORKFLOW.md：实现、测试、迁移和交付流程。
6. .codex/PROMPTS/bugfix.md 或 .codex/PROMPTS/feature.md：对应任务模板。

service/.codex/ 是后端项目的详细 Codex 规范源。修改认证、权限、数据库、响应契约或运行方式后，必须同步核对并更新相关规则。

## 项目技能

项目级可复用技能位于 `.agents/skills/`。根据任务按需读取对应 `SKILL.md`，不要一次性加载全部技能：

- `service-api-change`：路由、DTO、Controller、Service、DAO 和前后端 API 契约。
- `service-auth-rbac`：认证、Token、验证码、RBAC、管理员保护、租户和数据范围。
- `service-database-migration`：Alembic、MySQL schema、索引、外键、初始化 SQL 和权限 seed。
- `service-test-validation`：精准测试、完整测试、离线迁移检查和真实依赖验证边界。
- `service-production-readiness`：Docker Compose、启动顺序、健康检查、配置和发布风险。
- `service-code-review`：只读代码评审、缺陷优先级和发布风险证据。

技能只提供任务流程，不能覆盖本文件、仓库根目录规则或 `.codex/` 中的项目边界。若技能与当前源码冲突，以当前代码和测试核实后修正技能。
