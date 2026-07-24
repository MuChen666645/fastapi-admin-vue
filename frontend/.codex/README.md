# 前端 Codex 核心文件

本目录保存 Vue 前端项目的专属规则，用于提升代码生成的准确率、可维护性和安全性。

## 强制阅读顺序

开始实现前，必须按以下顺序阅读：

1. 仓库根目录 AGENTS.md：整体项目范围、规则优先级和安全边界。
2. frontend/AGENTS.md：前端规则入口。
3. AGENTS.md：前端实现规则和技术约束。
4. PROJECT.md：当前前端结构和后端接口事实。
5. ARCHITECTURE.md：前端分层、状态、传输和路由架构。
6. BOUNDARY.md：前端修改、安全和跨项目边界。
7. WORKFLOW.md：任务分析、实现、测试和交付流程。
8. PROMPTS/bugfix.md 或 PROMPTS/feature.md：对应的任务模板。

## 规范来源

- 用户明确要求优先级最高。
- 当前源码、后端 DTO、控制器、配置、迁移和测试是事实来源。
- 本目录的规则用于约束实现，不是接口事实本身。
- 旧文件 project-context.md、security-boundary.md 和 checklist.md 仅作兼容入口，不能与核心文件并行维护两套内容。

## 维护要求

当接口字段、路由、鉴权、文件、分页、依赖、构建工具或目录职责发生确认过的变化时，必须同步更新 PROJECT.md、ARCHITECTURE.md、BOUNDARY.md 或 WORKFLOW.md。

本目录不得保存真实密钥、令牌、生产数据、生成物、临时日志或调试输出。
