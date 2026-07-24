# 后端 Codex 入口

修改 service/ 下的文件前，必须按以下顺序阅读项目规则：

1. 仓库根目录 AGENTS.md：全局范围、安全和协作规则。
2. .codex/PROJECT.md：项目事实、目录职责和 API 约定。
3. .codex/ARCHITECTURE.md：应用生命周期、分层、会话和后台任务架构。
4. .codex/BOUNDARY.md：权限、租户、数据库、外部系统和禁止事项。
5. .codex/WORKFLOW.md：实现、测试、迁移和交付流程。
6. .codex/PROMPTS/bugfix.md 或 .codex/PROMPTS/feature.md：对应任务模板。

service/.codex/ 是后端项目的详细 Codex 规范源。修改认证、权限、数据库、响应契约或运行方式后，必须同步核对并更新相关规则。
