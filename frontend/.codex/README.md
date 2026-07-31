# 前端 Codex 文档入口

`frontend/.codex/` 保存前端专属的规则、事实、架构、边界、工作流和任务模板。文档只服务于当前前端项目，不处理后端实现；需要确认接口时可以只读核对后端 Controller、DTO、配置和测试。

## 阅读顺序

修改 `frontend/` 前按以下顺序阅读：

1. 仓库根目录 `AGENTS.md`：仓库范围、规则优先级和安全边界。
2. `frontend/AGENTS.md`：前端入口规则和当前实现摘要。
3. `.codex/AGENTS.md`：强制实现约束。
4. `.codex/PROJECT.md`：当前目录、脚本、环境和接口事实。
5. `.codex/ARCHITECTURE.md`：数据流、路由、Store、缓存和 Loading 架构。
6. `.codex/BOUNDARY.md`：文件范围、数据边界和安全禁止事项。
7. `.codex/WORKFLOW.md`：任务分析、实现、验证和交付流程。
8. `PROMPTS/feature.md` 或 `PROMPTS/bugfix.md`：功能开发或缺陷修复模板。

## 文件职责

| 文件              | 内容                   | 维护时机                               |
| ----------------- | ---------------------- | -------------------------------------- |
| `AGENTS.md`       | 强制规则和当前关键事实 | 规则、技术栈或核心边界变化             |
| `PROJECT.md`      | 可核对的项目事实       | 目录、依赖、脚本、环境或接口变化       |
| `ARCHITECTURE.md` | 模块职责和运行时数据流 | 分层、路由、Store、缓存或 Loading 变化 |
| `BOUNDARY.md`     | 安全与修改边界         | 权限、敏感数据、依赖或跨项目边界变化   |
| `WORKFLOW.md`     | 执行和验证流程         | 工具链、测试命令或交付流程变化         |
| `PROMPTS/*.md`    | 可复用任务模板         | 任务输入、验收或报告结构变化           |

## 文档维护原则

- 源码、测试、`package.json`、环境文件和构建配置优先于历史文档。
- 用当前文件路径和真实脚本，不记录已经删除的兼容入口。
- 文档中区分“当前事实”“强制规则”“目标方向”和“已知风险”，不能把目标结构写成已完成事实。
- 不在文档中写入密码、Token、密钥、生产数据、内部日志或不可公开的凭据。
- 文档变更完成后检查死路径、死命令、旧环境变量、重复规则和 `git diff --check`。

## 三条前端约束

- CSS 优先使用 UnoCSS utility class；`<style scoped>` 仅用于复杂的组件专属样式。
- 所有 `type`、`interface`、`enum` 声明集中到 `src/types/`，通过 `@/types` 统一导入。
- `src/views/` 下目录必须语义化并与后端 `component` 路径一致，页面私有组件放在页面自己的 `components/`。
