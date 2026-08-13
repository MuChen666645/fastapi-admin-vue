# 仓库 Codex 规范

`.codex/` 是前端和后端共同遵守的仓库级规范入口，负责跨项目事实、契约、边界、交付流程和任务模板。
前端和后端实现细节分别由 `frontend/.codex/` 与 `service/.codex/` 负责。

## 阅读顺序

1. `AGENTS.md`
2. `.codex/AGENTS.md`、`.codex/PROJECT.md`、`.codex/ARCHITECTURE.md`、`.codex/BOUNDARY.md`
3. `.codex/WORKFLOW.md` 与适用的根级 Skill
4. 目标项目的 `AGENTS.md`、`.codex/` 和领域 Skill
5. 受影响源码、DTO、类型、配置、迁移、调用方和测试

## 文档职责

| 文件 | 职责 |
| --- | --- |
| `AGENTS.md` | 仓库级强制边界和信息权威 |
| `PROJECT.md` | 两端已核验的运行、目录和接口事实 |
| `ARCHITECTURE.md` | HTTP 协作、身份、数据和交付架构 |
| `BOUNDARY.md` | 修改、信任、安全和外部依赖边界 |
| `WORKFLOW.md` | 端到端分析、实现、测试和交付流程 |
| `PROMPTS/` | 跨项目功能与缺陷任务模板 |

只记录当前、可验证、可维护的事实；不重复领域文档，不写历史任务、未核验字段、凭据、生产数据或生成物。

## 根级 Skill

`.agents/skills/` 按跨项目职责组织，不按开发、测试、预发或生产环境区分：

- `fullstack-contract-change`：前后端 API 契约变更。
- `fullstack-feature-delivery`：跨端业务功能交付编排。
- `fullstack-validation`：联动测试、构建、迁移和外部依赖验证。
- `repository-code-review`：仓库级只读评审和发布风险识别。

根级 Skill 只补充联动流程；进入单端实现后，必须切换到目标项目的领域 Skill。
