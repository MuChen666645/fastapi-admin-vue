---
name: service-auth-rbac
description: 追踪、实现或加固认证、JWT/会话、验证码、RBAC、管理员保护、租户隔离和数据范围检查。修改 module_admin/auth、权限判断、用户/角色写操作、Redis Token 状态、租户成员、部门范围或安全回归测试时使用。
---

# Service 认证与 RBAC

只要变更可能授予、保留、撤销或间接绕过资源访问，就使用本技能。所有读取、单条写入、批量、导入、重置、关联、租户切换、后台任务和运维入口都属于授权面。

## 工作流程

1. 先画出操作者和资源：用户、租户、角色、权限码、数据范围、资源所有权和资源状态。
2. 枚举所有相邻路径：单条、批量、导入、密码重置、状态修改、角色/菜单绑定、租户成员、定时任务、Worker、导出、文件、通知和运维入口。
3. 复用 `module_admin/auth/authorization.py`：
   - `Auth.router_auth`：完整 Token、会话、用户状态校验。
   - `Auth.login_status`：仅要求已登录。
   - `Auth.allow_password_change`：仅用于明确允许强制改密期间访问的流程。
   - `Auth.has_permission(...)`：权限码保护的管理操作。
4. 在 Service 边界执行授权，不能只依赖 Controller、前端按钮或前端路由守卫。
5. 同时执行所有适用的数据隔离：
   - 租户资源使用 `tenant_clause()` 和 `require_tenant_id()`。
   - 数据范围使用 `DataScopeService.resolve()`。
   - 文件、导出、通知、任务和在线会话再次检查所有权。
   - 部门祖先路径使用完整逗号分隔片段匹配，避免部门 ID `1` 错配到 `10`。
6. 管理员保护使用 `settings.ADMIN_ROLE_CODE`。检查直接角色字段和关联表绑定，不能只看一种来源。
7. 保留 Token 和 Redis 语义：不记录原始 JWT、Refresh Token、密码、验证码或密钥；不破坏 TTL、撤销、轮换、重放检测、锁定和有界降级行为。
8. 明确区分未登录、无权限、租户不匹配、资源不存在、会话过期/撤销和输入非法，不用返回空数据隐藏越权。
9. 同时覆盖允许路径和最近的绕过路径，加入跨租户、边界部门 ID、过期/撤销会话和 Redis 不可用场景测试。

## 禁止事项

- 不在 Controller 或 DAO 中新增第二套认证实现。
- 不硬编码 `admin`、固定用户 ID 或固定租户 ID 作为管理员判断。
- 不只保护列表接口而遗漏详情、批量、导入、重置和关联写入。
- 不让审计写入或后台任务复用业务请求会话。
- 不通过放宽校验、权限、类型或断言来使测试通过。

需要评审权限边界时读取 [authorization-surface-checklist.md](references/authorization-surface-checklist.md)。
