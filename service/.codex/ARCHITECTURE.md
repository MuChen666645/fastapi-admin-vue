# 系统架构

## 总体结构

```text
HTTP Client
    |
    v
FastAPI create_app()
    |
    +-- TrustedHost / CORS / Observability / Logger
    +-- SlowAPI / Idempotency / ResponseInterceptor
    +-- Exception handlers
    +-- /docs /redoc /openapi.json /metrics /static
    |
    v
AdminAPI: /api/v1 + controller router prefix
    |
    v
Controller -> Service -> DAO -> AsyncSession -> MySQL
                    |          |
                    |          +-- tenant_clause / DataScopeService
                    +-- Auth / Redis / file backend / task services
```

项目采用显式分层，但不是强制每个简单查询都必须创建新抽象。新增代码应把路由适配、业务规则、数据库访问和基础设施依赖放在正确边界内，避免 Controller 直接拼装复杂 SQL 或 DAO 负责权限决策。

## 应用组装

`main.create_app()` 创建独立的 FastAPI 实例并保存运行时状态：

- `app.state.settings`：当前应用配置
- `app.state.redis`：共享 Redis 客户端
- `app.state.mysql_engine`：MySQL AsyncEngine
- `app.state.mysql_session_factory`：后台任务和审计写入使用的会话工厂
- `app.state.scheduler`：可选 APScheduler 实例
- `app.state.metrics`：应用实例独立的 Prometheus registry
- `app.state.job_tasks`：显式注册的任务处理器

`AdminAPI` 在应用工厂末尾注册后台模块。每个 Controller 自己声明局部 `APIRouter(prefix=...)`，由 `module_admin/v1.py` 添加全局 `API_V1_PREFIX`。不要在单个 Controller 中重复写 `/api/v1`，也不要把管理路由直接注册到根应用绕过版本前缀。

## 生命周期

启动顺序：

1. 创建并检查 Redis 连接。
2. 创建并执行 `SELECT 1` 检查的 MySQL 引擎和会话工厂。
3. 同步带权限依赖的 API 路由目录到 `api_permission_catalog`。
4. 启动分片上传清理、通知投递、异步导出 Worker。
5. 按 `SCHEDULER_ENABLED` 启动 APScheduler，注册 `job_tasks` 并刷新持久化任务。
6. 执行应用启动钩子，然后开始接收请求。

关闭时取消后台循环、停止调度器、释放 MySQL 引擎，最后关闭 Redis。新增后台 Task 必须在生命周期的 `try/finally` 中有明确的取消和等待逻辑；不能创建无法回收的全局 Task。

数据库 schema 迁移不应放进 Web 应用生命周期。使用 `scripts.migrate_database`、Alembic 和 Compose 的 `fastapi-migrate` 服务，在 `fastapi-app` 启动前完成迁移。

## 请求和事务边界

带业务数据库依赖的路由由 `bind_request_mysql_session` 提供请求级 `AsyncSession`：

```text
request start
    -> session_factory()
    -> request.state.mysql = session
    -> Controller / Service / DAO
    -> success: commit
    -> exception: rollback
    -> request.state.mysql = None
```

约定如下：

- 业务请求使用 `request.state.mysql`，不要从模块全局创建或复用 AsyncSession。
- Service 和 DAO 可以在当前请求事务中 `flush`，最终提交由请求依赖负责；只有已有的独立任务流程才显式提交。
- 审计日志、生命周期任务、调度器、导出 Worker 和独立 Worker 使用 `app.state.mysql_session_factory` 创建独立会话，避免业务事务回滚时丢失审计或后台状态。
- 独立会话必须明确 `commit`、`rollback` 和关闭边界，不能借用已结束请求的 `request.state.mysql`。
- 健康检查不依赖业务请求级 MySQL 依赖；`/api/v1/health/live` 不检查外部服务，`/api/v1/health/ready` 单独检查 Redis、MySQL 和 `alembic_version`。

## Redis 和缓存

Redis 是进程间共享的基础设施，使用 `app.state.redis`，不是请求级 Redis 客户端。主要用途包括：

- Access Token 缓存和在线会话索引
- Refresh Token 轮换、重放检测和 Token family 撤销
- 验证码、验证码尝试次数和登录锁定
- SlowAPI 限流
- 幂等键状态
- Scheduler 分布式锁和锁续期
- 可选 Redis Streams 任务队列

认证在 Redis 不可用时有受限内存降级缓存，但它不是生产共享状态的替代品，必须保持有界 LRU，不能重新引入无限增长的进程缓存。不要把原始 JWT 或 Refresh Token 写入日志、数据库或 Redis key；现有实现使用 hash/索引 key。

## 认证、RBAC、租户和数据范围

认证依赖集中在 `module_admin/auth/authorization.py`：

- `Auth.router_auth` 验证 Authorization Header、JWT 签名、过期时间、缓存状态、用户状态和会话撤销状态。
- `Auth.login_status` 用于仅要求登录的接口。
- `Auth.allow_password_change` 用于密码强制修改期间仍允许的有限流程。
- `Auth.has_permission("system:user:list")` 等依赖用于按钮级 API 权限，并通过 `permission_code` 被 `PermissionSyncService` 发现。
- `ADMIN_ROLE_CODE` 是配置驱动的管理员角色码，不能在业务代码中硬编码 `admin` 作为唯一权限判断。

数据访问还必须同时考虑：

1. 当前租户：`tenant_clause()` 和 `require_tenant_id()`。
2. 操作者数据范围：`DataScopeService.resolve()` 返回全量、本部门、部门及子部门、自定义部门或本人范围。
3. 资源所有权：导出任务、文件、通知、在线会话等操作需要再次校验所属租户和操作者。

部门祖先路径必须做完整逗号分隔片段匹配，不能用会把部门 ID `1` 错配到 `10` 的简单 substring。任何新增用户、角色、部门、岗位、菜单、租户成员或敏感运维写路径，都要检查全部相邻写入口，而不是只保护一个 endpoint。

## 数据模型和迁移

- `entity/do` 是 SQLModel 表模型和关联表模型。
- `entity/dto` 是外部 API 合同，禁止直接把 DO 当作响应模型返回敏感字段。
- DAO 封装查询、分页、租户过滤、数据范围过滤和持久化细节。
- Alembic 版本位于 `alembic/versions`，当前迁移头以仓库实际 `head` 为准；不要在文档中硬编码过时版本号。
- `assets/sql/fastapi-admin.sql` 和 `assets/sql/schema-upgrade.sql` 属于初始化/历史安装资源，涉及 seed 或升级时必须保持幂等，且要同步测试。
- 新表、新字段、索引、唯一约束和权限目录都应有迁移、初始化/权限种子（如适用）及验证测试。

## 后台任务和文件

应用内任务包括分片清理、通知重试、导出轮询和可选调度器。`SCHEDULER_WORKER_MODE=inline` 在应用内执行注册处理器，`queue` 模式通过 Redis Streams 投递给独立的 `scripts.task_worker`。任务处理器必须显式注册，任务名必须与持久化 `task_name` 对应，并有超时、重试、分布式锁和失败告警边界。

文件服务支持本地目录和 OSS 两种后端，以及内容探测、扩展名限制、大小限制、可选病毒扫描、预签名 URL、分片上传和文本脱敏。文件 metadata 必须带租户和创建者约束，下载/删除不能只依赖文件 ID。

## 响应和可观测性

`ResponseInterceptor` 为 JSON 业务响应统一包装 `code`、`message`、`data`，错误响应还包括 `error_code`。`/docs`、`/redoc`、`/openapi.json`、静态资源和非 JSON 响应保持原样；文件、流和特殊响应通过 `X-Skip-Response-Wrapper` 跳过包装。

`ObservabilityMiddleware` 生成并返回 `X-Request-ID`、`X-Trace-ID`、`X-Span-ID` 和 `traceparent`，同时写入 Prometheus 指标。请求 ID 和 traceparent 必须经过格式校验；日志中记录路由模板和关联 ID，不记录密钥、JWT、密码或完整敏感 payload。

## 运行边界

- Web 进程负责 HTTP API、应用内清理循环、通知投递、导出轮询和可选调度器。
- `scripts.task_worker` 是独立进程入口，负责 queue 模式任务；不要让 Web 请求直接等待长时间任务完成。
- `fastapi-migrate` 负责部署前 schema 迁移；`fastapi-app` 依赖迁移成功后启动。
- `fastapi-edge` 是 production profile 的 Nginx 边缘入口，证书、反向代理和真实域名不属于本地单元测试范围。
- 健康检查只反映进程和关键依赖状态，不替代业务接口鉴权、数据库备份验证或第三方服务端到端验证。
