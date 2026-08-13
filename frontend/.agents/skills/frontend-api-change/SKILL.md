---
name: frontend-api-change
description: 实现、修改或评审 Vue 管理端领域 API 调用、响应 Parser、共享类型和页面数据交互。修改 frontend/src/api、src/types/api、请求参数、分页、上传下载或需要核对 FastAPI 接口契约时使用。
---

# Frontend API 变更

用于使前端调用严格匹配当前 FastAPI 接口，不以页面示例、旧文档或推测字段代替
Controller、DTO 和测试证据。

## 工作流程

1. 读取仓库 `AGENTS.md`、`frontend/AGENTS.md`、`frontend/.codex/` 和目标 API 的真实
   Controller、DTO、Service 行为及测试。
2. 先记录契约：`/api/v1` 路径、方法、Path/Query/Body/上传字段、成功和错误响应、分页、
   空值、认证、权限、租户或数据范围。
3. 在 `src/types/api/` 定义或调整蛇形字段 API 类型，并从 `@/types` 统一导出；不得让页面、
   Store、Router 或工具文件内联领域类型。
4. 在 `src/api/<domain>/index.ts` 编码请求，在同目录 `parsers.ts` 校验 unknown 响应；调用
   `requestJson` 或现有文件请求封装，不得在页面或 Store 直接使用 Alova、fetch、Axios、URL
   拼接或 Authorization。
5. 为状态枚举、日期、分页和 UI 字段提供明确适配，不得静默猜测、吞掉非法数据或用 Mock
   填充生产路径。
6. 检查全部调用方，保持查询、提交、删除、详情、上传下载、错误反馈和刷新行为一致；若契约
   变更，记录前后端联动影响。
7. 添加或调整 API/Parser 行为测试，覆盖请求参数、响应解析、空数据和关键错误分支。

## 质量边界

- 后端认证、授权、租户、数据范围和业务状态是最终权威，按钮和路由守卫不构成授权。
- 不放宽类型、不使用 `any`、`@ts-ignore` 或未验证断言掩盖契约差异。
- 不将 Token、密码、验证码、MFA、密钥或生产数据写入参数、日志、夹具或断言输出。
- 文件、流和原始响应必须复用现有跳过响应包装的调用约定。

## 验证

```powershell
pnpm exec vitest run src/__tests__/<domain>Api.spec.ts
pnpm run check
git diff --check
```

详细检查项见 [api-contract-checklist.md](references/api-contract-checklist.md)。
