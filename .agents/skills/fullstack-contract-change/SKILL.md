---
name: fullstack-contract-change
description: 设计、实现或评审本仓库 Vue 管理端与 FastAPI 服务之间的 API 契约变更。新增或修改 `/api/v1` 接口、DTO、响应结构、分页、文件传输、权限码、租户数据范围或任一端调用方时使用。
---

# 全栈契约变更

用于让接口变更在 service 和 frontend 之间保持一致。进入具体实现前，分别读取
`service/.agents/skills/service-api-change/` 与 `frontend/.agents/skills/frontend-api-change/`。

## 工作流程

1. 读取根和两端规则、目标 Controller、DTO、Service、DAO、前端 API/Parser、真实调用方和测试。
2. 建立契约表：方法、完整路径、Path/Query/Body/FormData、成功响应、分页、空值、业务错误、
   文件/流、响应包装、认证、权限、租户、数据范围、所有权、幂等和重试。
3. 后端按 `Controller -> Service -> DAO` 实现或核验；不得把 ORM 模型直接作为响应，也不得只靠
   前端限制保护资源。
4. 前端在 `src/types/api/`、`src/api/<domain>/` 和 `parsers.ts` 同步类型与调用；页面/Store 不得
   绕过 `request.ts` 或直接猜测字段。
5. 检查全部受影响操作：列表、详情、创建、编辑、删除、批量、状态、关联、导入导出、上传下载
   和后台任务入口。
6. 为两端各自的契约边界增加回归测试。没有真实端到端证据时，不得称联调完成。

## 禁止事项

- 不新增假接口、未核验枚举、静默 Mock、双重响应包装或平行认证机制。
- 不将 Token、密码、密钥、验证码、MFA 或生产数据写入文档、样例、日志和测试。
- 不把前端按钮、菜单或守卫视为服务端授权。

详细字段见 [contract-record.md](references/contract-record.md)。
