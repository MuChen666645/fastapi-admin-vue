---
name: repository-code-review
description: 以只读代码评审方式检查本仓库跨前后端改动中的 API 契约、权限租户、数据一致性、路由布局、迁移、构建、发布风险和测试缺口。用户要求全仓 review、审计或发布风险检查时使用。
---

# 仓库代码评审

默认只读，不修改代码。前端和后端单端评审分别读取对应 `frontend-code-review` 与
`service-code-review`，本 Skill 只关注跨项目影响。

## 工作流程

1. 确认评审范围和基线；未指定时读取当前工作区差异，不扩大到历史全仓扫描。
2. 读取根规则、两端适用规则、改动涉及的 Controller、DTO、Service、DAO、迁移、前端类型、
   API/Parser、Store、Router、Layout、配置和测试。
3. 沿真实请求链核对：页面/Store -> API/Parser -> request -> Controller -> Auth/Tenant ->
   Service -> DAO -> 数据库/外部副作用 -> 响应/错误反馈。
4. 按严重性优先检查：
   - 服务端认证、权限、管理员保护、租户、数据范围、资源所有权和事务绕过。
   - API 方法、路径、字段、分页、空值、错误、文件流、响应包装和前端调用的漂移。
   - 已应用迁移、seed、任务处理器、调度、缓存、并发、幂等和重复副作用风险。
   - Token/密钥泄露、XSS、动态 import、外链、上传、日志、浏览器存储和发布配置风险。
   - 路由、标签、缓存、Loading、抽屉、可访问性、构建和测试缺口。
5. 每个发现提供文件/行号、严重级别、真实路径、影响、根因和最小修复方向；区分确定缺陷和
   未验证风险。
6. 只执行不改变状态的验证，报告浏览器、Docker、MySQL、Redis、第三方和目标环境是否未执行。

输出格式和证据要求见 [review-output-checklist.md](references/review-output-checklist.md)。
