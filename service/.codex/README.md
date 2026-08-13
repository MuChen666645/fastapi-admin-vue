# 后端 Codex 规范

`service/.codex/` 保存 FastAPI 服务的运维开发规范。源码、测试、Alembic 版本、配置和
已核验运行行为优先于本文档。

## 阅读顺序

1. 仓库根目录 `AGENTS.md`、`.codex/README.md` 和适用的根级 Skill
2. `service/AGENTS.md`
3. `PROJECT.md`、`ARCHITECTURE.md`、`BOUNDARY.md`、`WORKFLOW.md`
4. `service/.agents/skills/` 下适用的项目 Skill
5. 关联 Controller、DTO、Service、DAO、模型、迁移、配置和测试

## 文档职责

| 文档 | 职责 |
| --- | --- |
| `PROJECT.md` | 已核验运行、目录、命令和迁移事实 |
| `ARCHITECTURE.md` | 分层、运行时、安全、租户和 Worker 职责 |
| `BOUNDARY.md` | 安全、数据库、外部系统和契约边界 |
| `WORKFLOW.md` | 实现、迁移、测试和交付流程 |

保持简洁并以证据为准。不得重复源码、历史任务记录、密钥、生成物或过期接口细节。
