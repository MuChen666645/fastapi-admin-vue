---
name: service-api-change
description: 实现、修改或评审 FastAPI 管理 API，包括路由、DTO、响应契约、权限和分层业务代码。修改 module_admin/controller、module_admin/service、module_admin/dao、module_admin/entity、module_admin/v1.py、响应拦截器，或新增前后端接口契约时使用。
---

# Service API 变更

用于让后端接口变更符合版本化路由、分层架构、认证授权、租户/数据范围、响应包装和测试约定。

## 工作流程

1. 修改前读取仓库根目录 `AGENTS.md`、`service/AGENTS.md` 和 `service/.codex/` 相关文件。若文档与当前源码、DTO、迁移或测试冲突，以当前代码为准并记录差异。
2. 搜索目标路由、DTO、权限码、Service 方法、DAO 查询和相邻 Controller。新增静态路由前，检查是否位于 `/{id}` 等动态路由之前。
3. 先明确接口契约：
   - HTTP 方法和完整 `/api/v1/...` 路径。
   - Query、Path、Body、上传字段、分页和响应字段。
   - 登录、权限、租户、数据范围和资源所有权要求。
   - 错误状态码、错误码和空数据语义。
   - 事务、幂等、重复提交和失败行为。
4. 按既有层次实现：
   - DTO/DO：负责校验和描述数据；不要直接把含敏感字段的 DO 作为响应。
   - DAO：负责 SQL、分页、持久化、租户条件和可复用过滤条件。
   - Service：负责业务规则、授权、编排和外部副作用。
   - Controller：负责依赖、参数、响应模型、路由元数据，并保持薄。
5. 管理路由必须通过 `module_admin/v1.py` 和 `AdminAPI` 注册。Controller 只使用模块局部前缀，不新增无版本旧路由。
6. 检查响应处理。JSON 业务响应通常由 `ResponseInterceptor` 包装；文件、流、HTML 和明确要求原始 JSON 的接口使用现有跳过包装机制，不新增第二套包装器。
7. 为变更增加针对性回归测试，至少覆盖无权限、租户不匹配、空数据、非法输入、重复提交以及适用的静态/动态路由冲突。
8. 如果契约变化，搜索前端真实调用方并记录影响。没有执行端到端验证时，不得声明联调完成。

## 项目约定

- HTTP 业务使用 `request.state.mysql`。不要在全局缓存请求 `AsyncSession`，也不要在 DAO 中关闭请求会话。
- 共享 Redis 从 `app.state.redis` 获取，保留现有 Token、验证码、限流、幂等、锁和任务 key 的 TTL 语义。
- 新增路由使用中文 `summary`；`Query`、`Path`、`File` 参数使用 `description`；DTO/SQLModel 字段使用 `Field(title=...)`。
- 管理员角色使用 `settings.ADMIN_ROLE_CODE`，认证和权限复用 `Auth`，不要在 Controller 中另写认证实现。
- 不把业务逻辑塞进 `main.py`、中间件或路由依赖，除非它确实属于横切能力。

## 验证

先运行最接近的测试，再根据是否影响认证、会话、DTO、响应或共享中间件扩大范围：

```powershell
$env:APP_ENV = "development"
$env:DEBUG = "true"
poetry run python -m pytest -q
git diff --check
```

需要完整语法检查时运行：

```powershell
poetry run python -m compileall -q main.py module_admin config middleware interceptors scripts alembic test
```

Docker、MySQL、Redis、OSS、SMTP、OIDC、LDAP 和前端验证必须单独报告。接口细节使用 [api-contract-checklist.md](references/api-contract-checklist.md)。
