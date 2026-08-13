# 前端 Codex 规范

本目录保存 `frontend/` 的可执行规范。源码、测试、包配置和已核验的后端
契约优先于本文档；本文档只说明如何基于这些事实安全地开展工作。

## 阅读顺序

1. 仓库根目录 `AGENTS.md`、`.codex/README.md` 和适用的根级 Skill
2. `frontend/AGENTS.md`
3. `.codex/AGENTS.md`
4. `.codex/PROJECT.md`、`.codex/ARCHITECTURE.md`、`.codex/BOUNDARY.md`
5. `.codex/WORKFLOW.md` 与适用的任务模板
6. 受影响源码、测试、API DTO 和后端 Controller 契约

## 文档职责

| 文档 | 职责 | 更新时机 |
| --- | --- | --- |
| `AGENTS.md` | 强制实现规则 | 架构或强制约束变化 |
| `PROJECT.md` | 已核验的项目事实和命令 | 依赖、脚本、路由、接口或目录变化 |
| `ARCHITECTURE.md` | 运行时职责和数据流 | 分层、状态、路由或 Loading 变化 |
| `BOUNDARY.md` | 安全和修改边界 | 信任、授权、持久化或依赖边界变化 |
| `WORKFLOW.md` | 交付和验证流程 | 评审或验证流程变化 |

只记录简洁、可验证的当前事实。不得写入历史任务记录、未核验接口字段、凭据、
生产数据、生成物或已废弃兼容路径。

## 项目 Skill

项目级 Skill 位于 `frontend/.agents/skills/`，按任务只读取一个或少量相关 Skill：

- `frontend-api-change`：领域 API、Parser、共享类型、分页、上传下载和前后端契约。
- `frontend-auth-rbac`：登录、刷新、会话、守卫、权限指令、租户相关 UI 与安全存储。
- `frontend-layout-routing`：静态/动态路由、BasicLayout、标签、缓存、Loading 和系统设置抽屉。
- `frontend-test-validation`：聚焦测试、静态检查、构建、失败诊断与验证边界。
- `frontend-production-readiness`：Vite 构建、静态资源、运行配置、发布审计和部署风险。
- `frontend-code-review`：只读缺陷评审、契约回归、权限体验和发布风险。

Skill 以职责组织，不按开发、测试、预发或生产环境划分。它们不替代源码核验、后端授权或
本目录中的项目边界。
