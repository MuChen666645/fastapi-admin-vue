# FastAPI Admin Vue Service

> 中文 | [English](./README.en.md)

FastAPI Admin Vue Service 是 FastAPI Admin Vue 的后台管理服务，面向企业管理场景提供统一身份认证、角色权限、租户隔离、组织管理、系统参数、消息中心、文件管理、定时任务和运维观测能力。

服务通过 HTTP 契约与同仓库 `frontend/` 协作。认证、授权、租户、数据范围、业务状态和数据一致性以后端实现为最终依据。

## 能力范围

| 领域 | 能力 | API 前缀 |
| --- | --- | --- |
| 认证与账号 | 登录、刷新令牌、验证码、MFA、密码策略和找回密码 | `/api/v1/user`、`/api/v1/captcha` |
| RBAC | 用户、角色、菜单、按钮权限、字段权限和数据范围 | `/api/v1/user`、`/api/v1/role`、`/api/v1/menu` |
| 组织管理 | 部门、岗位、字典类型和字典数据 | `/api/v1/dept`、`/api/v1/post`、`/api/v1/dict` |
| 多租户 | 租户生命周期、成员关系和租户切换 | `/api/v1/tenant` |
| 系统管理 | 系统参数、消息、日志和在线会话 | `/api/v1/config`、`/api/v1/message`、`/api/v1/log`、`/api/v1/online` |
| 文件与导出 | 本地或 OSS 文件、分片上传、异步导出和文本脱敏 | `/api/v1/file` |
| 作业与运维 | Cron 作业、执行日志、备份、健康检查和指标 | `/api/v1/job`、`/api/v1/ops/backup`、`/api/v1/health`、`/metrics` |
| 外部认证 | OIDC/OAuth 与 LDAP 登录 | `/api/v1/auth` |

初始化菜单在“系统管理”下提供“系统参数”和“租户管理”。对应组件分别为 `system/config/index` 与 `system/tenant/index`。菜单仅是服务端导航元数据，前端必须提供同名视图并接入真实 API 后才能开放页面。

## 架构与目录

```text
HTTP Client -> FastAPI -> /api/v1 Controller -> Service -> DAO -> MySQL
                                      |             |
                                      +-- Auth/Redis +-- 租户与数据范围过滤
```

| 目录 | 职责 |
| --- | --- |
| `main.py` | 应用工厂、生命周期和中间件组装 |
| `config/` | 环境配置、MySQL、Redis、限流 |
| `module_admin/controller/` | API 路由和依赖注入 |
| `module_admin/service/` | 业务编排、事务协作和后台任务 |
| `module_admin/dao/` | 查询、分页、持久化和作用域过滤 |
| `module_admin/entity/do/` | SQLModel 数据表模型 |
| `module_admin/entity/dto/` | Pydantic 请求/响应模型 |
| `alembic/` | 版本化数据库迁移 |
| `assets/sql/` | 初始化和升级 SQL |
| `scripts/` | 迁移、备份和独立 Worker 入口 |
| `test/` | 单元、API 和集成测试 |

Controller 只负责请求解析、依赖和响应元数据；业务规则放在 Service，DAO 只负责数据访问。HTTP 请求使用 `request.state.mysql` 的请求级会话，成功统一提交，异常统一回滚；调度、审计、导出和 Worker 使用独立会话工厂。

## API 与响应约定

- 管理 API 统一使用 `API_V1_PREFIX`，默认 `/api/v1`；不提供无版本前缀兼容路由。
- Controller 只声明模块前缀，如 `/tenant`、`/config`，全局前缀由 `module_admin/v1.py` 统一注册。
- JSON 业务响应统一为 `{ "code": 200, "message": "success", "data": ... }`；错误响应使用统一错误结构并包含 `error_code`。文件、流和静态资源保持原始响应。
- `/docs`、`/redoc`、`/openapi.json` 是接口契约来源；非开发环境由 `DOCS_AUTH_TOKEN` 保护。
- `GET /api/v1/health/live` 只检查进程存活；`GET /api/v1/health/ready` 同时检查 MySQL、Redis 和迁移状态。

完整字段、状态码、权限依赖和分页结构以当前 OpenAPI 与 DTO 为准，客户端不得根据旧 README 臆造接口。

## 认证、授权与租户

受保护接口使用 Bearer Token：

```http
Authorization: Bearer <access_token>
```

服务校验 JWT 签名、有效期、缓存状态、用户状态、密码版本和会话撤销状态。Access/Refresh Token 支持轮换，重复使用旧 Refresh Token 会撤销对应令牌族。验证码、登录失败锁定、密码策略、强制改密和 MFA 均由认证服务统一处理。

- 路由通过 `Depends(Auth.has_permission("system:resource:action"))` 执行按钮级权限校验。
- `permissions` 是权限目录；`menu_type = F` 的按钮菜单通过 `perms` 与权限编码关联，`role_menu` 维护角色授权。
- `*:*:*` 为平台超级管理员通配权限；平台租户操作还要求 `Auth.platform_admin_status`。
- 字段权限使用 `field:<resource>:<field>`；数据范围支持全量、本部门、部门及子部门、自定义部门和本人。
- 业务读写同时按当前租户、数据范围和资源所有权校验；前端隐藏菜单不能替代后端授权。

## 环境与配置

运行要求：Python 3.11+、Poetry 1.8+、MySQL 8.x、Redis 6.x+，容器化部署需要 Docker Compose。

应用根据 `APP_ENV` 选择 `.env.development`、`.env.staging` 或 `.env.production`；进程环境变量优先。`APP_ENV_FILE` 仅用于 Compose 的 `env_file`。

```powershell
Copy-Item .env.development.example .env.development
$env:APP_ENV = "development"
$env:DEBUG = "true"
```

重点配置：

| 分类 | 配置 |
| --- | --- |
| 应用 | `APP_ENV`、`DEBUG`、`API_V1_PREFIX`、`HOSTS`、`ORIGINS` |
| MySQL | `MYSQL_HOST`、`MYSQL_POST`、`MYSQL_USERNAME`、`MYSQL_PASSWORD`、`MYSQL_DATABASES` |
| Redis | `REDIS_HOST`、`REDIS_POST`、`REDIS_USERNAME`、`REDIS_PASSWORD`、`REDIS_DB` |
| 安全 | `SECRET_KEY`、`ADMIN_ROLE_CODE`、`PASSWORD_*`、`MFA_*`、`RATE_LIMIT_*` |
| 调度 | `SCHEDULER_ENABLED`、`SCHEDULER_WORKER_MODE`、`SCHEDULER_DEFAULT_TIMEOUT_SECONDS`、`SCHEDULER_DEFAULT_MAX_RETRIES` |
| 文件与观测 | `FILE_*`、`OSS_*`、`OTEL_*`、`DOCS_AUTH_TOKEN`、`METRICS_AUTH_TOKEN` |

生产和预发布必须关闭 Debug、限制 Host/CORS、配置 Redis 认证及文档/指标令牌。真实密码、Token、密钥、OSS 凭据和生产地址不得进入仓库。

## 本地开发

```bash
poetry install
docker compose --env-file .env.development up -d fastapi-mysql fastapi-redis
poetry run python -m scripts.migrate_database
poetry run uvicorn main:app --host 0.0.0.0 --port 3000 --reload
```

访问地址：`http://127.0.0.1:3000`；OpenAPI：`/docs`；ReDoc：`/redoc`；就绪探针：`/api/v1/health/ready`。

## 数据库迁移与初始化

数据库结构只通过 Alembic 管理，不在应用启动时执行 DDL：

```bash
poetry run python -m scripts.migrate_database
poetry run alembic upgrade head --sql > migration.sql
```

`assets/sql/fastapi-admin.sql` 是显式执行的初始化脚本，用于写入默认租户、内置账号、角色、组织、菜单、权限目录、角色菜单关系和字典数据。脚本使用固定业务 ID、事务和 `INSERT IGNORE`，可重复执行，且不会由应用生命周期自动执行。

```bash
mysql --host 127.0.0.1 --port 3306 --user YOUR_MYSQL_USER --password=YOUR_MYSQL_PASSWORD --database fastapi_admin < assets/sql/fastapi-admin.sql
```

已有数据库执行 Alembic 即可。迁移 `0028_tenant_and_system_parameter_menus` 会补齐默认租户的租户管理目录和八个租户操作按钮，将菜单 `351` 规范为“系统参数”，并为管理员角色补齐新增内置菜单授权。

## 容器化部署

迁移服务成功后，FastAPI 应用才应启动：

```bash
docker compose --env-file .env.development up -d --build
docker compose --env-file .env.staging up -d --build
docker compose --env-file .env.production --profile production up -d --build
```

生产发布前完成密钥注入、数据库备份、TLS、Host/CORS 收敛和就绪探针验证。常用诊断：

```bash
docker compose --env-file .env.development logs -f fastapi-migrate
docker compose --env-file .env.development logs -f fastapi-app
docker compose --env-file .env.development config
```

## 调度与后台任务

- `SCHEDULER_ENABLED=true` 才会创建 APScheduler。
- `/api/v1/job` 中的 `task_name` 必须与 `create_app(job_tasks={...})` 注册键完全一致；持久化作业不会自动创建处理器。
- `SCHEDULER_WORKER_MODE=inline` 在 Web 进程执行，`queue` 模式通过 Redis Streams 投递给 `scripts.task_worker`。
- Redis 分布式锁避免多实例重复执行；任务支持超时、重试、暂停/恢复和执行日志。
- 长耗时业务使用调度器、独立 Worker 或异步导出，不阻塞 HTTP 请求线程。

```python
from main import create_app

app = create_app(job_tasks={"example.task": lambda args: "ok"})
```

## 可观测性与安全

- 请求返回 `X-Request-ID`、`X-Trace-ID`、`X-Span-ID` 和 `traceparent`。
- `/metrics` 提供 HTTP、依赖就绪、任务和通知指标，非开发环境由 `METRICS_AUTH_TOKEN` 保护。
- `OTEL_ENABLED=true` 时向 `OTEL_EXPORTER_OTLP_ENDPOINT` 导出链路；任务失败可通过 `ALERT_WEBHOOK_URL` 告警。
- 所有变更保留幂等、认证、权限、租户、数据范围和资源归属校验；批量操作记录审计快照。
- 文件上传校验扩展名、大小和内容签名；敏感系统参数加密存储并仅返回掩码。
- 备份与恢复属于受控运维操作；在线恢复默认关闭，需维护窗口、运维令牌和 MFA 同时满足。

## 质量验证

```powershell
$env:APP_ENV = "development"
$env:DEBUG = "true"

poetry run python -m compileall -q main.py module_admin config middleware interceptors scripts alembic test
poetry run python -m pytest -q -m "not integration"
poetry run black --check path/to/changed_file.py
poetry run isort --check-only --profile black .
poetry run flake8 --max-line-length=88 .
```

真实依赖集成测试需先启动 MySQL/Redis：

```bash
docker compose --env-file .env.development up -d fastapi-mysql fastapi-redis
poetry run python -m scripts.migrate_database
RUN_INTEGRATION_TESTS=1 poetry run python -m pytest -q -m integration
```

## 常见问题

**环境变量缺失**：确认 `APP_ENV` 对应文件存在，且 MySQL、Redis、`SECRET_KEY` 等必填项已注入。

**调度器未启用或处理器未注册**：设置 `SCHEDULER_ENABLED=true` 并重启，确认 `task_name` 与 `create_app(job_tasks={...})` 的键完全一致。

**菜单存在但页面不可用**：检查角色菜单/按钮权限，并确认前端存在菜单 `component` 指向的视图文件；后端菜单不会生成前端页面。

**就绪探针失败**：检查 MySQL、Redis 和 `alembic_version`；`live` 成功不代表依赖已就绪。

## 许可证

This repository does not currently declare a license. Add an appropriate license and third-party compliance statement before external distribution or commercial delivery.
