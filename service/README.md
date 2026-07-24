# FastAPI Admin Vue Service

> 中文 | [English](#english)

FastAPI Admin Vue Service 是一个基于 **FastAPI + SQLModel + MySQL + Redis** 的后台管理系统服务端工程。项目采用分层结构组织业务代码，包含用户、角色、菜单、验证码、JWT 鉴权、按钮级权限控制、统一响应拦截、请求日志、限流、静态资源和 Docker 部署配置。

## 功能特性

- FastAPI 异步 Web API 服务
- SQLModel + SQLAlchemy AsyncSession 数据访问
- MySQL 数据持久化
- Redis 缓存、验证码存储、Token 二级缓存与跨进程共享限流
- JWT 登录认证、Token 内存/Redis 校验与按钮级接口权限校验
- Access/Refresh Token 轮换、停用用户拦截、强制改密、密码策略、MFA 和密码找回
- 用户、角色、菜单管理模块，菜单按钮权限同步到权限目录
- 若依风格 RBAC 权限模型，支持超级管理员通配权限 `*:*:*`
- 租户隔离、字段级权限、权限变更审计和数据范围控制
- 图片验证码生成与校验；明文数字验证码接口已停用
- 统一响应拦截与异常处理，未知错误返回脱敏的 500 响应
- 请求 ID、W3C traceparent 链路关联和结构化 JSON 日志
- 文件签名校验、可选 ClamAV 扫描、分片上传、预签名 URL 和文本脱敏
- Excel 用户/角色/字典导入导出、通知收件箱、数据库备份和恢复工具
- 持久化异步 Excel 导出任务，可查询状态并按租户下载结果文件
- Redis 分布式任务锁、超时/重试/暂停、Prometheus 指标和可选 OTLP 链路
- 本地/阿里云 OSS 文件上传下载、系统参数、通知公告和定时任务
- Prometheus 指标监控，可通过 `/metrics` 抓取
- SlowAPI 请求限流
- Swagger/OpenAPI 在线接口文档，按接口展示完整响应体 DTO
- Dockerfile 与 Docker Compose 本地编排
- Poetry 依赖管理
- pre-commit、Black、isort、flake8、Commitizen 工程规范

## 技术栈


| 分类        | 技术                   |
| ----------- | ---------------------- |
| Web 框架    | FastAPI                |
| ASGI Server | Uvicorn                |
| 数据模型    | Pydantic, SQLModel     |
| 数据库      | MySQL                  |
| 数据库驱动  | aiomysql               |
| 缓存        | Redis                  |
| 鉴权        | PyJWT                  |
| 密码加密    | passlib                |
| 分页        | fastapi-pagination     |
| 限流        | slowapi                |
| 日志        | loguru                 |
| 指标        | prometheus-client      |
| 对象存储    | oss2                   |
| 定时任务    | APScheduler            |
| 图片处理    | Pillow                 |
| 依赖管理    | Poetry                 |
| 容器化      | Docker, Docker Compose |

## 目录结构

```text
.
|-- assets/                 # SQL 初始化脚本、字体等资源
|   |-- font/
|   `-- sql/
|-- config/                 # 环境变量、MySQL、Redis 配置
|-- interceptors/           # 异常拦截器
|-- middleware/             # 日志、响应处理中间件
|-- module_admin/           # 后台管理业务模块
|   |-- auth/               # JWT 与权限校验
|   |-- controller/         # API 路由层
|   |-- dao/                # 数据访问层
|   |-- entity/
|   |   |-- do/             # SQLModel 数据表模型
|   |   `-- dto/            # Pydantic 请求/响应模型
|   `-- service/            # 业务逻辑层
|-- static/                 # 静态资源目录
|-- alembic/                # 版本化数据库迁移
|-- scripts/                # 部署和迁移入口
|-- test/                   # 测试目录
|-- utils/                  # 通用工具
|-- main.py                 # FastAPI 应用入口
|-- pyproject.toml          # Poetry 与工具配置
|-- Dockerfile
`-- docker-compose.yml
```

## 架构约定

项目按以下分层组织代码：

```text
Controller -> Service -> DAO -> Database
```

- `controller`：仅负责路由定义、参数接收、依赖注入。
- `service`：负责业务逻辑、流程编排、权限相关业务判断。
- `dao`：负责数据库查询与持久化操作。
- `entity/dto`：定义 API 请求与响应数据结构。
- `entity/do`：定义数据库表模型。

### 运行时流程

```text
请求
  -> 关联 ID / 观测中间件
  -> 日志、限流、统一响应中间件
  -> 路由依赖注入 MySQL 请求会话
  -> Controller -> Service -> DAO
  -> MySQL / Redis / 文件存储
```

- `main.create_app()` 负责组装中间件、异常处理器、静态资源、分页和后台路由。
- 应用启动时建立 Redis、MySQL 连接，并按配置启动定时任务；数据库结构由 `scripts.migrate_database` 和 Alembic 管理，不在应用启动阶段执行 DDL。
- `/api/v1/health/live` 只表示进程可以响应请求；`/api/v1/health/ready` 会检查 Redis、MySQL 和 `alembic_version`，所有依赖就绪后才返回成功。
- 业务请求使用 `request.state.mysql` 的请求级事务；日志审计使用独立会话，避免业务事务回滚时丢失异常记录。

### 注释与文档规范

- 生产代码中的模块、类、功能函数和关键辅助函数使用中文 docstring，优先说明职责、输入输出、事务边界和安全约束。
- 配置常量、权限常量、缓存 Key 前缀、正则表达式和运行时状态使用紧邻定义的中文行内注释说明用途。
- Pydantic/SQLModel 字段通过 `title` 或 `description` 说明接口字段；路由通过 `summary` 说明接口用途，详细请求响应结构以 OpenAPI 为准。
- 注释解释“为什么”以及跨模块约束，不重复翻译显而易见的代码；修改行为时同步更新 docstring 和 README。
- 新增业务逻辑应遵循 `Controller -> Service -> DAO` 边界，并为权限、数据范围、缓存一致性和资源释放等副作用补充说明。

## 环境要求

- Python 3.11+
- Poetry 1.8+
- MySQL 8.x
- Redis 6.x+
- Docker / Docker Compose，可选

## 环境变量

项目根据 `APP_ENV` 选择 `.env.development`、`.env.staging` 或 `.env.production`。环境变量会覆盖环境文件中的值；如果直接使用 `uvicorn` 启动，请确保选定环境文件存在或变量已经注入到当前进程环境中。

```env
# FastAPI
APP_ENV=development
APP_ENV_FILE=.env.development
DEBUG=true
TITLE=FastAPI Admin
SUMMARY=FastAPI, SQLModel, MySQL and Redis admin service.
VERSION=0.0.1
OPENAPI_URL=/openapi.json
API_V1_PREFIX=/api/v1

# MySQL
MYSQL_HOST=127.0.0.1
MYSQL_POST=3306
MYSQL_USERNAME=fastapi_app
MYSQL_PASSWORD=your_mysql_password
MYSQL_ROOT_PASSWORD=your_mysql_root_password
MYSQL_DATABASES=fastapi_admin
TIMEZONE=Asia/Shanghai

# Redis
REDIS_HOST=127.0.0.1
REDIS_USERNAME=
REDIS_PASSWORD=your_redis_password
REDIS_POST=6379
REDIS_DB=0

# Aliyun OSS
ACCESS_KEY_ID=your_access_key_id
ACCESSKEY_SECRET=your_access_key_secret
OSS_ENDPOINT=
OSS_BUCKET=
OSS_PREFIX=uploads

# File storage
FILE_STORAGE_BACKEND=local
FILE_UPLOAD_DIR=uploads
FILE_MAX_SIZE_BYTES=10485760
FILE_PRESIGN_TTL_SECONDS=300
FILE_CONTENT_SNIFF_ENABLED=true
FILE_VIRUS_SCAN_ENABLED=false
FILE_REDACTION_ENABLED=false
FILE_CHUNK_TTL_SECONDS=86400
CLAMAV_HOST=clamav
CLAMAV_PORT=3310
FILE_ALLOWED_EXTENSIONS=[".jpg",".jpeg",".png",".gif",".webp",".pdf",".doc",".docx",".xls",".xlsx",".zip"]

# Scheduler
SCHEDULER_ENABLED=false
SCHEDULER_TIMEZONE=Asia/Shanghai
SCHEDULER_DEFAULT_TIMEOUT_SECONDS=300
SCHEDULER_LOCK_TTL_SECONDS=900
SCHEDULER_DEFAULT_MAX_RETRIES=0
EXPORT_WORKER_ENABLED=true
EXPORT_POLL_SECONDS=2
EXPORT_TASK_TTL_SECONDS=86400
SCHEDULER_WORKER_MODE=inline

# 独立任务 Worker
WORKER_ENABLED=true
TASK_QUEUE_STREAM=fastapi:tasks
TASK_QUEUE_GROUP=fastapi-workers
TASK_WORKER_CONSUMER=local-worker
TASK_HANDLER_MODULE=module_admin.service.task_handlers
TASK_HEARTBEAT_SECONDS=15
TASK_LOCK_RENEW_SECONDS=30

# 异步导出
EXPORT_WORKER_ENABLED=true
EXPORT_POLL_SECONDS=2
EXPORT_TASK_TTL_SECONDS=86400

# Observability, backup, and optional identity providers
OTEL_ENABLED=false
OTEL_SERVICE_NAME=fastapi-admin
OTEL_EXPORTER_OTLP_ENDPOINT=
OTEL_EXPORTER_OTLP_HEADERS=
LOG_RETENTION_DAYS=30
ALERT_WEBHOOK_URL=
NOTIFICATION_WEBHOOK_URL=
NOTIFICATION_SMS_WEBHOOK=
NOTIFICATION_RETRY_MAX_ATTEMPTS=5
NOTIFICATION_RETRY_BASE_SECONDS=30
NOTIFICATION_DELIVERY_LEASE_SECONDS=300
BACKUP_DIR=backups
BACKUP_ENCRYPTION_KEY=
BACKUP_ONLINE_RESTORE_ENABLED=false
BACKUP_RESTORE_MAINTENANCE_MODE=false
BACKUP_RESTORE_OPERATIONS_TOKEN=
BACKUP_RETENTION_DAYS=30
BACKUP_TIMEOUT_SECONDS=900
IDEMPOTENCY_RETENTION_DAYS=2
BATCH_AUDIT_RETENTION_DAYS=90
NOTIFICATION_RETENTION_DAYS=30
RETENTION_CLEANUP_INTERVAL_SECONDS=3600
SECRET_MANAGER_ACTIVE_VERSION=v1
SECRET_MANAGER_KEYS=
OIDC_ENABLED=false
OIDC_AUTHORIZATION_URL=
OIDC_TOKEN_URL=
OIDC_USERINFO_URL=
OIDC_CLIENT_ID=
OIDC_CLIENT_SECRET=
OIDC_REDIRECT_URI=
OIDC_SCOPES=openid profile email
OIDC_ISSUER=
OIDC_AUDIENCE=
OIDC_JWKS_URL=
LDAP_ENABLED=false
LDAP_SERVER_URL=
LDAP_BASE_DN=
LDAP_BIND_DN=
LDAP_BIND_PASSWORD=
LDAP_USER_FILTER=(uid={username})

# 邮件/短信找回密码
PASSWORD_RESET_SMS_WEBHOOK=
SMTP_HOST=
SMTP_PORT=465
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_FROM=

# Optional
SECRET_KEY=replace_with_a_stable_random_secret
ACCESS_TOKEN_EXPIRE_MINUTES=3600
ADMIN_ROLE_CODE=admin
RATE_LIMIT_DEFAULT=300/minute
RATE_LIMIT_LOGIN=10/minute
RATE_LIMIT_CAPTCHA=30/minute
RATE_LIMIT_REFRESH_TOKEN=30/minute
RATE_LIMIT_PASSWORD_RESET=5/minute
RATE_LIMIT_EXTERNAL_AUTH=10/minute
CAPTCHA_TTL_SECONDS=300
CAPTCHA_MAX_VERIFY_ATTEMPTS=5
LOGIN_MAX_FAILED_ATTEMPTS=5
LOGIN_IP_LOCK_SECONDS=300
LOGIN_ACCOUNT_MAX_FAILED_ATTEMPTS=5
LOGIN_ACCOUNT_LOCK_SECONDS=900
PASSWORD_MIN_LENGTH=12
PASSWORD_REQUIRE_UPPERCASE=true
PASSWORD_REQUIRE_LOWERCASE=true
PASSWORD_REQUIRE_DIGIT=true
PASSWORD_REQUIRE_SPECIAL=true
PASSWORD_HISTORY_COUNT=5
PASSWORD_MAX_AGE_DAYS=90
PASSWORD_FORCE_CHANGE_ON_CREATE=true
REFRESH_TOKEN_EXPIRE_DAYS=30
MFA_ISSUER=FastAPI Admin
PASSWORD_RESET_TOKEN_TTL_SECONDS=900
PASSWORD_RESET_EMAIL_ENABLED=false
READINESS_TIMEOUT_SECONDS=5
HOSTS=["*"]
TRUSTED_PROXIES=[]
ORIGINS=["*"]
MEDOTHS=["*"]
HEADERS=["*"]
CREDENTIALS=false
```

> 注意：`MYSQL_POST`、`REDIS_POST`、`MEDOTHS`、`ACCESSKEY_SECRET` 是当前代码中的实际配置项名称，请保持一致。

> Compose 固定使用 `fastapi-mysql` 和 `fastapi-redis` 作为服务名。`MYSQL_PASSWORD` 用于应用账号 `MYSQL_USERNAME`，`MYSQL_ROOT_PASSWORD` 仅用于 MySQL root 健康检查和管理操作；Compose 首次初始化时会创建应用账号。

> 除 `DATABASE_SCHEMA_VERSION` 等代码不变量外，部署参数不再提供代码级默认值。请复制对应的 `.example` 文件并填写所有值；更换 `SECRET_KEY` 会使已签发的 JWT 失效。

## 本地开发

### 1. 安装依赖

```bash
poetry install
```

### 2. 选择本地运行环境

应用根据 `APP_ENV` 读取 `.env.<APP_ENV>`；`APP_ENV_FILE` 仅由 Docker Compose 用于选择容器的 `env_file`。首次使用时复制对应示例并填写配置：

```powershell
Copy-Item .env.development.example .env.development
Copy-Item .env.staging.example .env.staging
Copy-Item .env.production.example .env.production
```

直接在宿主机运行时，staging/production 示例中的 `MYSQL_HOST=fastapi-mysql` 和 `REDIS_HOST=fastapi-redis` 应改为本机可访问的地址，例如 `127.0.0.1`；这两个服务名只适用于容器网络。

PowerShell 启动命令：

```powershell
# development
$env:APP_ENV = "development"
poetry run uvicorn main:app --host 0.0.0.0 --port 3000 --reload

# staging
$env:APP_ENV = "staging"
poetry run uvicorn main:app --host 0.0.0.0 --port 3000

# production
$env:APP_ENV = "production"
poetry run uvicorn main:app --host 0.0.0.0 --port 3000
```

Bash/Linux 启动命令：

```bash
APP_ENV=development poetry run uvicorn main:app --host 0.0.0.0 --port 3000 --reload
APP_ENV=staging poetry run uvicorn main:app --host 0.0.0.0 --port 3000
APP_ENV=production poetry run uvicorn main:app --host 0.0.0.0 --port 3000
```

### 3. 准备 MySQL 与 Redis

可以使用本机服务，也可以通过 Docker Compose 只启动依赖服务：

```bash
docker compose --env-file .env.development up -d fastapi-mysql fastapi-redis
```

### 4. 创建数据库

如果没有使用 `docker-compose.yml` 中的默认数据库，请手动创建数据库：

```sql
CREATE DATABASE fastapi_admin DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

数据库结构由 `fastapi-migrate` 或 `scripts.migrate_database` 在服务启动前迁移。没有 `alembic_version` 的旧安装会先标记为 `0001_initial_schema`，再升级到当前 head；持久化数据库卷不会因环境文件变化自动更换 MySQL 密码，改密前请先备份。

### 5. 迁移和初始化数据

`APP_ENV` 决定迁移使用的数据库配置。运行迁移后，再显式执行初始化数据脚本：

```bash
poetry run python -m scripts.migrate_database
mysql --host 127.0.0.1 --port 3306 --user YOUR_MYSQL_USER --password=YOUR_MYSQL_PASSWORD --database fastapi_admin < assets/sql/fastapi-admin.sql
```

服务启动成功后访问：

- API 服务：`http://127.0.0.1:3000`
- Swagger 文档：`http://127.0.0.1:3000/docs`
- ReDoc 文档：`http://127.0.0.1:3000/redoc`
- OpenAPI JSON：`http://127.0.0.1:3000/openapi.json`

## Docker 部署

### 1. 选择 Docker 环境

先复制并填写对应的环境文件。`--env-file` 同时提供 Compose 插值变量，`APP_ENV_FILE` 再让应用、迁移、MySQL 和 Redis 容器加载同一份配置。

development：

```bash
docker compose --env-file .env.development up -d --build
```

staging：

```bash
docker compose --env-file .env.staging up -d --build
```

production：准备证书文件 `certs/fullchain.pem` 和 `certs/privkey.pem`，然后启用 `fastapi-edge` profile：

```bash
docker compose --env-file .env.production --profile production up -d --build
```

首次部署后执行初始化数据脚本（迁移服务会先完成 schema 迁移）：

```bash
docker compose --env-file .env.development exec -T fastapi-mysql sh -c 'mysql -uroot -p"$MYSQL_ROOT_PASSWORD" fastapi_admin' < assets/sql/fastapi-admin.sql
```

staging/production 将命令中的 `.env.development` 替换为对应环境文件。生产环境不要使用开发环境配置或 `--watch`。

### 2. 查看日志

```bash
docker compose logs -f fastapi-app
```

### 3. 停止服务

```bash
docker compose down
```

默认端口映射：


| 服务    | 容器端口 | 本机端口 |
| ------- | -------- | -------- |
| FastAPI | 3000     | 127.0.0.1:3000 |
| MySQL   | 3306     | 127.0.0.1:3306 |
| Redis   | 6379     | 127.0.0.1:6379 |
| Nginx (production profile) | 80/443 | 80/443 |

基础 Compose 配置仅将 FastAPI、MySQL 和 Redis 绑定到本机；生产 profile 通过 Nginx 暴露 80/443，并将 HTTPS 请求转发到 FastAPI。生产环境部署前请修改所有 `.env.production.example` 占位符、准备 TLS 证书，并限制 `HOSTS` 与 CORS 来源。

## API 模块


| 模块     | 路由前缀   | 说明                                                     |
| -------- | ---------- | -------------------------------------------------------- |
| 用户     | `/api/v1/user`    | 用户创建、登录、自助修改密码、管理员重置密码、用户信息查询 |
| 角色     | `/api/v1/role`    | 角色创建、列表查询、详情、更新、删除                     |
| 菜单     | `/api/v1/menu`    | 菜单创建、菜单树/列表查询、详情、更新、删除              |
| 部门     | `/api/v1/dept`    | 部门树查询、创建、更新、删除                             |
| 岗位     | `/api/v1/post`    | 岗位列表查询、创建、更新、删除                           |
| 字典     | `/api/v1/dict`    | 字典类型和字典数据的增删改查                             |
| 日志     | `/api/v1/log`     | 登录、操作、异常日志查询和删除                           |
| 在线用户 | `/api/v1/online`  | 在线会话查询、单会话和用户会话强制退出                   |
| 验证码   | `/api/v1/captcha` | 图片验证码与校验；明文数字验证码接口返回 `410`           |
| 健康检查 | `/api/v1/health`  | 存活探针和 MySQL/Redis/schema 就绪探针                   |
| 指标监控 | `/metrics` | Prometheus HTTP 请求数、状态码和耗时指标                 |
| 文件存储 | `/api/v1/file`    | 本地或阿里云 OSS 文件上传、下载和删除                     |
| 系统参数 | `/api/v1/config`  | 系统参数键值配置                                         |
| 通知公告 | `/api/v1/notice`  | 公告增删改查                                             |
| 定时任务 | `/api/v1/job`     | Cron 任务管理、手动执行和执行日志                        |
| 外部认证 | `/api/v1/auth`    | OIDC/OAuth 与 LDAP 登录                                  |
| 数据备份 | `/api/v1/ops/backup` | 受权限保护的数据库备份接口                              |
| 静态资源 | `/static`  | 静态文件访问                                             |

完整请求参数与响应结构请以 Swagger 文档为准。

`GET /api/v1/captcha/image` 返回 `captcha_id` 和 Base64 图片。用户名登录、手机号登录及 `GET /api/v1/captcha/verify` 必须同时提交 `captcha_id` 与图片中的验证码。验证码 ID 绑定获取时的客户端 IP，校验成功后立即失效；连续错误达到 `CAPTCHA_MAX_VERIFY_ATTEMPTS` 次后也会失效，有效期由 `CAPTCHA_TTL_SECONDS` 控制。

## 认证方式

登录接口返回 JWT Token。调用受保护接口时，在请求头中携带：

```http
Authorization: Bearer <access_token>
```

Token 使用 `HS256` 算法签名，过期时间由 `ACCESS_TOKEN_EXPIRE_MINUTES` 控制。登录成功后，Token 会同时写入进程内存和 Redis，Redis Key 格式为 `auth:token:{sha256(token)}`。

受保护接口会先校验内存缓存，未命中时再查询 Redis；两级缓存都不存在时返回 `401 Token Not Found`。缓存命中后仍会继续校验 JWT 签名、过期时间和用户状态，Redis TTL 与 Token 过期时间保持一致。

## 权限与响应模型

- 路由通过 `Depends(Auth.has_permission("权限标识"))` 做按钮级权限控制，例如 `system:menu:edit`。
- `permissions` 表作为权限目录，菜单表中 `menu_type = F` 的按钮权限通过 `menu.perms` 与 `permissions.code` 打通。
- 新增或修改按钮菜单时会同步写入/更新权限目录；删除按钮菜单时，如果权限标识未被其他按钮菜单使用，会同步清理对应权限。
- 角色通过 `role_menu` 关联菜单和按钮权限，接口鉴权时按用户角色、菜单按钮和权限目录共同判断。
- 超级管理员权限 `*:*:*` 存放在 `permissions` 表中，不作为菜单数据返回；拥有超级权限时，用户信息接口只返回 `*:*:*` 权限标识。
- `PUT /api/v1/user/{user_id}/password` 用于输入旧密码的自助修改；`PUT /api/v1/user/{user_id}/reset-password` 使用 `system:user:resetPwd` 权限执行管理员重置，成功后会使目标用户已有会话失效。
- 登录会在签发 Token 前检查用户状态；已停用用户直接返回“用户已停用”，不会先获得可用 Token。
- 请求校验失败返回结构化的 `422` 响应，字段错误位于 `data.errors`，客户端不应依赖异常字符串解析。
- MySQL 连接 URL 使用 SQLAlchemy `URL.create()` 组装，用户名或密码包含 `@`、`:`、`/` 等字符时无需手动转义。
- 接口运行时统一返回 `{ "code": 200, "message": "success", "data": ... }`；未知异常只返回脱敏的 500 响应，详细堆栈写入服务日志。Swagger 中每个接口使用 `ApiResponseDto[T]` 描述实际响应体，避免响应体展示为 `Any`。

## 常用命令

```bash
# 安装依赖
poetry install

# 启动开发服务
poetry run uvicorn main:app --host 0.0.0.0 --port 3000 --reload

# 运行测试
poetry run python -m pytest -q

# 运行单元测试并检查 60% 覆盖率阈值
poetry run python -m pytest -q -m "not integration" --cov --cov-report=term-missing

# 启动本地真实 MySQL/Redis（测试数据会使用随机后缀并在测试后清理）
docker compose up -d fastapi-mysql fastapi-redis
poetry run python -m scripts.migrate_database

# 运行 MySQL/Redis 集成测试
RUN_INTEGRATION_TESTS=1 poetry run python -m pytest -q -m integration

# 运行不使用服务 mock 的真实后台 API 集成测试
RUN_INTEGRATION_TESTS=1 poetry run python -m pytest -q test/test_admin_api_async.py

# 在临时数据库中验证在线迁移降级和重新升级
poetry run alembic downgrade base
poetry run python -m scripts.migrate_database

# 验证加密备份、备份结构和独立数据库恢复演练
poetry run python -m scripts.backup_database backup
poetry run python -m scripts.backup_database verify <filename>
poetry run python -m scripts.backup_database rehearse <filename>

# 在测试或多实例部署中创建独立应用
from main import create_app
application = create_app()

# 显式注册定时任务处理器，/api/v1/job 中的 task_name 必须匹配。
application = create_app(job_tasks={"example.task": lambda args: "ok"})

# 代码格式化
poetry run black .
poetry run isort .

# 代码检查
poetry run flake8 .

# 安装 pre-commit hooks
poetry run pre-commit install

# Commitizen 提交
poetry run cz commit
```

## 代码规范

- 遵循 `Controller -> Service -> DAO -> Database` 分层。
- 路由层保持轻量，业务逻辑放入 `service`。
- 数据库访问集中在 `dao`。
- 请求与响应模型使用 Pydantic。
- 数据表模型使用 SQLModel。
- 异步接口优先使用 `async/await`。
- 类、功能函数和关键辅助函数使用中文 docstring，说明职责和重要副作用。
- 配置常量、权限编码、缓存 Key 和生命周期状态使用中文行内注释。
- 接口字段使用 `Field(title=..., description=...)`，请求参数使用 `description`，路由使用中文 `summary`。
- 注释只解释设计原因和跨模块约束；代码行为变化时同步更新 README、OpenAPI 元数据和测试说明。
- 提交信息建议遵循 Conventional Commits：

```text
feat: add user login
fix: handle redis timeout
refactor: simplify role service
docs: update readme
test: add user service tests
chore: update dependencies
```

## 初始化数据

`assets/sql/fastapi-admin.sql` 是部署阶段显式执行的种子脚本，用于写入初始用户、角色、菜单、权限目录和角色菜单关系等基础数据。应用生命周期不会执行该脚本；脚本使用 `INSERT IGNORE`，可以安全重复执行。

## 常见问题

### 1. 本地启动时报环境变量缺失

请确认 MySQL、Redis、OSS 等必需变量已经注入到进程环境中。Docker Compose 会读取当前目录 `.env`；直接 `uvicorn` 启动时，请根据实际启动目录确认 Pydantic 能读取到环境文件，或改用系统环境变量。

### 2. MySQL 连接失败

请检查：

- `MYSQL_HOST` 与 `MYSQL_POST` 是否正确。
- 数据库是否已经创建。
- 用户名和密码是否正确。
- MySQL 容器是否已启动。

### 3. Redis 认证失败

请检查：

- `REDIS_PASSWORD` 是否与 Redis 服务一致。
- Redis 是否启用了用户名认证。
- `REDIS_USERNAME` 为空时是否符合当前 Redis 配置。

### 4. 接口返回 401

请确认请求头中携带了合法 Token：

```http
Authorization: Bearer <access_token>
```

如果请求头正确但仍返回 401，请继续确认：

- Token 是否仍存在于内存或 Redis 缓存中。
- Redis 服务是否正常连接，且 `auth:token:` 前缀的缓存未被清理。
- `SECRET_KEY` 是否在服务重启前后保持一致。
- Token 是否已超过 `ACCESS_TOKEN_EXPIRE_MINUTES` 配置的有效期。

### 5. 接口请求过快被限制

项目默认对每个 IP 限制 `300/minute`，允许后台页面并发加载；用户名和手机号登录限制为 `10/minute`，验证码获取及校验限制为 `30/minute`。刷新 Token、密码找回和外部认证分别使用独立限流：`RATE_LIMIT_REFRESH_TOKEN`、`RATE_LIMIT_PASSWORD_RESET`、`RATE_LIMIT_EXTERNAL_AUTH`。可通过这些环境变量调整。

同一 IP 在 `LOGIN_IP_LOCK_SECONDS` 秒内连续输错密码达到 `LOGIN_MAX_FAILED_ATTEMPTS` 次后，将禁止用户名和手机号登录，锁定时间同为 `LOGIN_IP_LOCK_SECONDS` 秒。默认连续错误 5 次锁定 300 秒，密码校验正确会清除尚未触发锁定的失败计数。

## License

当前仓库未声明 License。请在发布或商用前补充许可证信息。

---

## 安全与运维

### 认证与密码策略

- 登录成功返回短期 `access_token` 和可轮换的 `refresh_token`。调用 `POST /api/v1/user/token/refresh` 后，旧刷新令牌立即失效；重复使用旧令牌会撤销整个令牌族。
- 已停用用户在签发令牌前被拒绝。受保护接口还会检查用户状态、密码版本和强制改密状态。
- 支持 TOTP MFA：`POST /api/v1/user/mfa/setup`、`/api/v1/user/mfa/enable`、`/api/v1/user/mfa/disable`。登录表单可提交 `mfa_code`，也可使用一次性恢复码。
- 密码策略由 `PASSWORD_*` 配置控制，包括最小长度、大小写/数字/特殊字符、历史密码数量、最大有效期和首次改密。
- IP 和账号维度均支持失败登录锁定，配置项为 `LOGIN_MAX_FAILED_ATTEMPTS`、`LOGIN_IP_LOCK_SECONDS`、`LOGIN_ACCOUNT_MAX_FAILED_ATTEMPTS` 和 `LOGIN_ACCOUNT_LOCK_SECONDS`。
- `POST /api/v1/user/password/forgot` 和 `/api/v1/user/password/reset` 支持邮箱或短信找回密码。生产环境必须配置 SMTP 或短信 Webhook，接口不会在响应中返回明文找回令牌。
- 可选 OIDC/OAuth 和 LDAP 登录，配置 `OIDC_*` 或 `LDAP_*` 后使用 `/api/v1/auth/oidc/start`、`/api/v1/auth/oidc/callback` 和 `/api/v1/auth/ldap/login`。OIDC 必须配置 `OIDC_ISSUER`、`OIDC_AUDIENCE`、`OIDC_JWKS_URL`，回调会校验签名、发行方、受众、Nonce、PKCE 和 `email_verified`；外部登录仍需提交 MFA 验证码。

### 租户与权限

- 用户、角色、菜单、部门、岗位、字典、通知、文件、任务、配置和日志记录带有 `tenant_id`，查询和写入会按当前租户隔离。
- 应用启动时自动同步带有 `Auth.has_permission(...)` 的路由到 `api_permission_catalog`。
- 字段权限编码格式为 `field:<resource>:<field>`，通过角色 DTO 的 `field_permission_codes` 绑定；没有字段权限时，用户敏感字段会被隐藏。
- 角色和菜单权限变更写入 `permission_change_versions`，保存操作者、版本号以及变更前后快照。
- 支持租户成员关系、租户切换、软删除和乐观锁；写入租户上下文缺失时默认拒绝。
- 写请求支持 `Idempotency-Key`，批量用户/角色操作记录前后快照，业务异常会回滚事务。

### 文件、通知和运维接口

- 文件支持内容签名识别、可选 ClamAV 扫描、OSS 预签名 URL、本地/OSS 存储、分片上传和文本脱敏。
- 当 `FILE_VIRUS_SCAN_ENABLED=true` 时，必须提供可访问的 ClamAV 服务，并通过 `CLAMAV_HOST`/`CLAMAV_PORT` 配置地址；默认 Compose 文件不包含 ClamAV 容器。
- 分片流程：`POST /api/v1/file/chunk/init`、`PUT /api/v1/file/chunk/{upload_id}/{chunk_index}`、`POST /api/v1/file/chunk/complete`。未完成的分片记录和临时目录会按 `FILE_CHUNK_TTL_SECONDS` 定期清理。
- 系统参数中 `secret`、`password`、`sensitive` 类型会加密存储，列表、详情和按键查询只返回掩码；请勿将敏感值写入日志或提交到环境示例文件。
- 文本脱敏接口为 `GET /api/v1/file/redacted/{file_id}`，需显式启用 `FILE_REDACTION_ENABLED`。
- 用户、角色和字典支持 Excel 导入导出；导入仍执行 DTO、密码策略、租户和重复数据校验。
- 用户、角色和字典支持异步导出：调用对应的 `/export/async` 创建任务，再轮询 `/export/tasks/{task_id}`，完成后通过 `/export/tasks/{task_id}/download` 下载。
- 通知支持指定收件人、收件箱、未读筛选和已读标记：`GET /api/v1/notice/inbox/list`、`POST /api/v1/notice/{notice_id}/read`。
- 通知支持收件箱、Webhook、邮件和短信渠道，使用 `NOTIFICATION_DELIVERY_LEASE_SECONDS` 防止多实例重复认领，并按 `NOTIFICATION_RETRY_MAX_ATTEMPTS` 和退避间隔重试。
- 数据库备份可通过 `poetry run python -m scripts.backup_database backup` 或受平台超级管理员保护的 `/api/v1/ops/backup/create` 执行；`verify` 命令和 `/api/v1/ops/backup/verify` 可在恢复前检查加密备份结构，`rehearse` 命令和 `/api/v1/ops/backup/rehearse` 会在 `BACKUP_REHEARSAL_DATABASE` 指定的临时库中实际恢复并自动删除。在线恢复接口默认禁用，仅在受控维护窗口、运维令牌和 MFA 二次验证全部满足时启用。备份使用 Fernet 加密并按保留天数清理。

### 定时任务与可观测性

- APScheduler 负责触发调度，`SCHEDULER_WORKER_MODE=queue` 时通过 Redis Streams 投递到独立 `fastapi-worker`；Worker 使用心跳、空闲消息接管和任务锁续租保证可靠执行。
- Redis `SET NX EX` 负责多实例互斥；任务支持超时、重试、暂停/恢复和执行日志。
- `SCHEDULER_DEFAULT_TIMEOUT_SECONDS`、`SCHEDULER_LOCK_TTL_SECONDS` 和 `SCHEDULER_DEFAULT_MAX_RETRIES` 控制默认执行行为；任务 DTO 也可以单独设置超时和重试次数。
- `/metrics` 除 HTTP 指标外，还暴露 MySQL/Redis 就绪状态、任务执行次数/耗时和告警投递状态。配置 `ALERT_WEBHOOK_URL` 后，任务失败会发送结构化告警。
- 配置 `OTEL_ENABLED=true` 和 `OTEL_EXPORTER_OTLP_ENDPOINT` 后启用 FastAPI 链路并通过 OTLP 导出。日志文件按 `LOG_RETENTION_DAYS` 保留。非开发环境的 `/docs`、`/redoc`、`/openapi.json` 和 `/metrics` 分别使用 `DOCS_AUTH_TOKEN`、`METRICS_AUTH_TOKEN` 保护。

### 数据库迁移与 Docker 排障

当前数据库迁移头为 `0025_security_consistency`。迁移入口会自动创建或扩展 `alembic_version.version_num` 到 `VARCHAR(64)`，兼容旧数据库默认的 `VARCHAR(32)`；部署后请检查 `/api/v1/health/ready` 的 `schema` 状态为 `ok`。

```bash
docker compose --env-file .env.development up -d --build
docker compose --env-file .env.development logs -f fastapi-migrate
poetry run python -m scripts.migrate_database
```

如果出现 `1045 Access denied`，说明 MySQL 持久卷中的账号密码与当前环境文件不一致。持久卷不会因修改 `.env` 自动改密：保留数据时使用原 root 密码轮换 `fastapi_app`；仅开发数据可丢失时才使用 `docker compose down -v` 后重新初始化。不要为解决 `1045` 直接删除生产数据卷。

## English

> [中文](#fastapi-admin-vue-service) | English

FastAPI Admin Vue Service is a backend service for an admin management system built with **FastAPI, SQLModel, MySQL, and Redis**. It follows a layered architecture and includes user management, role management, menu management, captcha, JWT authentication, button-level authorization, response interception, request logging, rate limiting, static files, and Docker deployment support.

## Features

- Async FastAPI Web API service
- SQLModel + SQLAlchemy AsyncSession data access
- MySQL persistence
- Redis cache, captcha storage, token cache, and cross-process shared rate limiting
- JWT login authentication, memory/Redis token validation, and button-level route authorization
- Rotating access/refresh tokens, disabled-user rejection, password policy, forced password change, MFA, and password recovery
- User, role, and menu management modules with menu button permission synchronization
- RuoYi-style RBAC model with super-admin wildcard permission `*:*:*`
- Tenant isolation, field-level permissions, data scopes, and permission-change auditing
- Image captcha generation/verification; the plaintext numeric endpoint is disabled
- Unified response interception and exception handling with sanitized 500 responses
- Request IDs, W3C `traceparent` correlation, and structured JSON logs
- File signature checks, optional ClamAV scanning, chunked uploads, presigned URLs, and text redaction
- Excel import/export for users, roles, and dictionaries, notice inboxes, and encrypted database backups
- Tenant memberships, tenant switching, soft deletion, optimistic locking, strict tenant-scoped queries, and rollback-safe writes
- Idempotency keys for mutating requests and before/after audit snapshots for batch operations
- Redis Streams task queue with an independent Worker, worker heartbeats, lock renewal, timeout, and retry controls
- Versioned Secret Manager encryption, masked sensitive config, key rotation, encrypted backup verification, and restore rehearsal tooling
- Inbox, webhook, email, and SMS notification delivery with bounded exponential retries
- Redis-distributed job locks, timeout/retry/pause controls, Prometheus metrics, and optional OTLP traces
- Local/Aliyun OSS file upload and download, system config, notices, and scheduled jobs
- Prometheus metrics available at `/metrics` (protected by `METRICS_AUTH_TOKEN` outside development)
- SlowAPI rate limiting
- All admin routes use the versioned `/api/v1` prefix.
- Swagger/OpenAPI API documentation with concrete per-route response DTOs; operations endpoints require `DOCS_AUTH_TOKEN` outside development
- Dockerfile and Docker Compose setup
- Poetry dependency management
- pre-commit, Black, isort, flake8, and Commitizen workflow

## Tech Stack


| Category              | Technology             |
| --------------------- | ---------------------- |
| Web Framework         | FastAPI                |
| ASGI Server           | Uvicorn                |
| Data Models           | Pydantic, SQLModel     |
| Database              | MySQL                  |
| Database Driver       | aiomysql               |
| Cache                 | Redis                  |
| Authentication        | PyJWT                  |
| Password Hashing      | passlib                |
| Pagination            | fastapi-pagination     |
| Rate Limiting         | slowapi                |
| Logging               | loguru                 |
| Image Processing      | Pillow                 |
| Dependency Management | Poetry                 |
| Containerization      | Docker, Docker Compose |

## Project Structure

```text
.
|-- assets/                 # SQL seed scripts, fonts, and other assets
|   |-- font/
|   `-- sql/
|-- config/                 # Environment, MySQL, and Redis configuration
|-- interceptors/           # Exception interceptors
|-- middleware/             # Logging and response middleware
|-- module_admin/           # Admin business module
|   |-- auth/               # JWT and authorization logic
|   |-- controller/         # API route layer
|   |-- dao/                # Data access layer
|   |-- entity/
|   |   |-- do/             # SQLModel table models
|   |   `-- dto/            # Pydantic request/response models
|   `-- service/            # Business logic layer
|-- static/                 # Static files
|-- alembic/                # Versioned database migrations
|-- scripts/                # Deployment and migration entrypoints
|-- test/                   # Test directory
|-- utils/                  # Shared utilities
|-- main.py                 # FastAPI application entry
|-- pyproject.toml          # Poetry and tooling configuration
|-- Dockerfile
`-- docker-compose.yml
```

## Architecture

The project follows this layered flow:

```text
Controller -> Service -> DAO -> Database
```

- `controller`: defines routes, receives parameters, and wires dependencies.
- `service`: contains business logic, orchestration, and permission-related rules.
- `dao`: handles database queries and persistence.
- `entity/dto`: defines API request and response schemas.
- `entity/do`: defines database table models.

### Runtime Flow

```text
Request
  -> correlation and observability middleware
  -> logging, rate limiting, and response middleware
  -> request-scoped MySQL session dependency
  -> Controller -> Service -> DAO
  -> MySQL / Redis / file storage
```

- `main.create_app()` assembles middleware, exception handlers, static files, pagination, and admin routes.
- Startup creates Redis and MySQL clients and optionally starts the scheduler. Alembic migrations are applied by `scripts.migrate_database`, not by application startup DDL.
- `/api/v1/health/live` only reports process liveness. `/api/v1/health/ready` checks Redis, MySQL, and `alembic_version` before returning success.
- Business requests use the request-scoped transaction in `request.state.mysql`; audit logs use an independent session so rollback does not hide the failure record.

### Documentation and Comment Rules

- Production modules, classes, functional methods, and important helpers use Chinese docstrings that explain responsibility, inputs/outputs, transaction boundaries, and security constraints.
- Configuration constants, permission constants, cache-key prefixes, regular expressions, and runtime state use adjacent comments explaining their purpose.
- Pydantic/SQLModel fields use `title` or `description`; routes use `summary`. The generated OpenAPI document is the source of truth for full schemas.
- Comments explain why and cross-module constraints rather than restating obvious code. Update docstrings and README when behavior changes.
- New business logic follows `Controller -> Service -> DAO` boundaries and documents side effects involving permissions, data scope, cache consistency, and resource cleanup.

## Requirements

- Python 3.11+
- Poetry 1.8+
- MySQL 8.x
- Redis 6.x+
- Docker / Docker Compose, optional

## Environment Variables

The service selects one profile with `APP_ENV`: `development`, `staging`, or `production`. Development loads `.env.development`; shared environments load `.env.staging` or `.env.production`, which should be created locally from the matching example file. Environment variables exported by the process always take precedence over files.

```env
# Profile selection
APP_ENV=development
APP_ENV_FILE=.env.development

# FastAPI
DEBUG=true
TITLE=FastAPI Admin
SUMMARY=FastAPI, SQLModel, MySQL and Redis admin service.
VERSION=0.0.1
OPENAPI_URL=/openapi.json

# MySQL
MYSQL_HOST=127.0.0.1
MYSQL_POST=3306
MYSQL_USERNAME=fastapi_app
MYSQL_PASSWORD=your_mysql_password
MYSQL_ROOT_PASSWORD=your_mysql_root_password
MYSQL_DATABASES=fastapi_admin
TIMEZONE=Asia/Shanghai

# Redis
REDIS_HOST=127.0.0.1
REDIS_USERNAME=
REDIS_PASSWORD=your_redis_password
REDIS_POST=6379
REDIS_DB=0

# Aliyun OSS
ACCESS_KEY_ID=your_access_key_id
ACCESSKEY_SECRET=your_access_key_secret
OSS_ENDPOINT=
OSS_BUCKET=
OSS_PREFIX=uploads

# File storage
FILE_STORAGE_BACKEND=local
FILE_UPLOAD_DIR=uploads
FILE_MAX_SIZE_BYTES=10485760
FILE_PRESIGN_TTL_SECONDS=300
FILE_CONTENT_SNIFF_ENABLED=true
FILE_VIRUS_SCAN_ENABLED=false
FILE_REDACTION_ENABLED=false
FILE_CHUNK_TTL_SECONDS=86400
CLAMAV_HOST=clamav
CLAMAV_PORT=3310
FILE_ALLOWED_EXTENSIONS=[".jpg",".jpeg",".png",".gif",".webp",".pdf",".doc",".docx",".xls",".xlsx",".zip"]

# Scheduler
SCHEDULER_ENABLED=false
SCHEDULER_TIMEZONE=Asia/Shanghai
SCHEDULER_DEFAULT_TIMEOUT_SECONDS=300
SCHEDULER_LOCK_TTL_SECONDS=900
SCHEDULER_DEFAULT_MAX_RETRIES=0

# Observability, backup, and optional identity providers
OTEL_ENABLED=false
OTEL_SERVICE_NAME=fastapi-admin
OTEL_EXPORTER_OTLP_ENDPOINT=
OTEL_EXPORTER_OTLP_HEADERS=
LOG_RETENTION_DAYS=30
ALERT_WEBHOOK_URL=
BACKUP_DIR=backups
BACKUP_ENCRYPTION_KEY=
BACKUP_REHEARSAL_DATABASE=fastapi_admin_restore_rehearsal
BACKUP_ONLINE_RESTORE_ENABLED=false
BACKUP_RESTORE_MAINTENANCE_MODE=false
BACKUP_RESTORE_OPERATIONS_TOKEN=
BACKUP_RETENTION_DAYS=30
BACKUP_TIMEOUT_SECONDS=900
IDEMPOTENCY_RETENTION_DAYS=2
BATCH_AUDIT_RETENTION_DAYS=90
NOTIFICATION_RETENTION_DAYS=30
RETENTION_CLEANUP_INTERVAL_SECONDS=3600
OIDC_ENABLED=false
OIDC_AUTHORIZATION_URL=
OIDC_TOKEN_URL=
OIDC_USERINFO_URL=
OIDC_CLIENT_ID=
OIDC_CLIENT_SECRET=
OIDC_REDIRECT_URI=
OIDC_SCOPES=openid profile email
OIDC_ISSUER=
OIDC_AUDIENCE=
OIDC_JWKS_URL=
LDAP_ENABLED=false
LDAP_SERVER_URL=
LDAP_BASE_DN=
LDAP_BIND_DN=
LDAP_BIND_PASSWORD=
LDAP_USER_FILTER=(uid={username})

# Security and optional settings
SECRET_KEY=generate_a_random_secret_at_least_32_characters_long
ACCESS_TOKEN_EXPIRE_MINUTES=3600
ADMIN_ROLE_CODE=admin
RATE_LIMIT_DEFAULT=300/minute
RATE_LIMIT_LOGIN=10/minute
RATE_LIMIT_CAPTCHA=30/minute
RATE_LIMIT_REFRESH_TOKEN=30/minute
RATE_LIMIT_PASSWORD_RESET=5/minute
RATE_LIMIT_EXTERNAL_AUTH=10/minute
CAPTCHA_TTL_SECONDS=300
CAPTCHA_MAX_VERIFY_ATTEMPTS=5
LOGIN_MAX_FAILED_ATTEMPTS=5
LOGIN_IP_LOCK_SECONDS=300
LOGIN_ACCOUNT_MAX_FAILED_ATTEMPTS=5
LOGIN_ACCOUNT_LOCK_SECONDS=900
PASSWORD_MIN_LENGTH=12
PASSWORD_REQUIRE_UPPERCASE=true
PASSWORD_REQUIRE_LOWERCASE=true
PASSWORD_REQUIRE_DIGIT=true
PASSWORD_REQUIRE_SPECIAL=true
PASSWORD_HISTORY_COUNT=5
PASSWORD_MAX_AGE_DAYS=90
PASSWORD_FORCE_CHANGE_ON_CREATE=true
REFRESH_TOKEN_EXPIRE_DAYS=30
MFA_ISSUER=FastAPI Admin
PASSWORD_RESET_TOKEN_TTL_SECONDS=900
PASSWORD_RESET_EMAIL_ENABLED=false
PASSWORD_RESET_SMS_WEBHOOK=
SMTP_HOST=
SMTP_PORT=465
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_FROM=
READINESS_TIMEOUT_SECONDS=5
HOSTS=["localhost","127.0.0.1"]
TRUSTED_PROXIES=[]
ORIGINS=["http://localhost:5173"]
MEDOTHS=["GET","POST","PUT","DELETE","OPTIONS"]
HEADERS=["*"]
CREDENTIALS=false
```

> Note: `MYSQL_POST`, `REDIS_POST`, `MEDOTHS`, and `ACCESSKEY_SECRET` are the actual setting names used by the current codebase. Keep them unchanged unless the code is updated.

> Compose uses `fastapi-mysql` and `fastapi-redis` as fixed service names. `MYSQL_PASSWORD` belongs to the application account `MYSQL_USERNAME`; `MYSQL_ROOT_PASSWORD` is reserved for MySQL root health checks and administration. Compose creates the application account on first initialization.

> Except for code invariants such as `DATABASE_SCHEMA_VERSION`, deployment settings have no code-level defaults. Copy the matching `.example` file and fill every value. A `SECRET_KEY` change invalidates previously issued JWTs.

## Environment Profiles

| Profile | Configuration | Production checks |
| --- | --- | --- |
| Development | `.env.development` | Allows local-only defaults and debug logging |
| Staging | `.env.staging` from `.env.staging.example` | Requires generated secrets, `DEBUG=false`, and restricted hosts/origins |
| Production | `.env.production` from `.env.production.example` | Requires generated secrets, `DEBUG=false`, and restricted hosts/origins |

For staging or production, copy the example file, replace every `REPLACE_WITH_...` value, then start with the matching `APP_ENV`. The service also supports secret-store injection through process environment variables, so the real environment file does not need to be copied into the image or container. Do not commit it.

## Local Development

### 1. Install dependencies

```bash
poetry install
```

### 2. Select the local environment

The application reads `.env.<APP_ENV>` according to `APP_ENV`. `APP_ENV_FILE` is used by Docker Compose to select the container `env_file`; it does not select the file for a direct `uvicorn` process. Copy the matching example and fill in its values before starting:

```powershell
Copy-Item .env.development.example .env.development
Copy-Item .env.staging.example .env.staging
Copy-Item .env.production.example .env.production
```

When running directly on the host, change `MYSQL_HOST=fastapi-mysql` and `REDIS_HOST=fastapi-redis` in staging/production configurations to reachable host addresses such as `127.0.0.1`; those service names are available only inside the Compose network.

PowerShell commands:

```powershell
# development
$env:APP_ENV = "development"
poetry run uvicorn main:app --host 0.0.0.0 --port 3000 --reload

# staging
$env:APP_ENV = "staging"
poetry run uvicorn main:app --host 0.0.0.0 --port 3000

# production
$env:APP_ENV = "production"
poetry run uvicorn main:app --host 0.0.0.0 --port 3000
```

Bash/Linux commands:

```bash
APP_ENV=development poetry run uvicorn main:app --host 0.0.0.0 --port 3000 --reload
APP_ENV=staging poetry run uvicorn main:app --host 0.0.0.0 --port 3000
APP_ENV=production poetry run uvicorn main:app --host 0.0.0.0 --port 3000
```

### 3. Prepare MySQL and Redis

You can use local services or start only the dependency services with Docker Compose:

```bash
docker compose --env-file .env.development up -d fastapi-mysql fastapi-redis
```

### 4. Create the database

If you are not using the default database from `docker-compose.yml`, create it manually:

```sql
CREATE DATABASE fastapi_admin DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Database schema changes are managed by the migration service before the application starts. Existing installations without `alembic_version` are detected, stamped at `0001_initial_schema`, and upgraded to the current head. A persistent database volume does not rotate its MySQL password when an environment file changes; rotate the credential explicitly or use a new volume only after taking a backup.

### 5. Migrate and seed data

`APP_ENV` determines which database configuration the migration uses. Run the migration and then load the seed data explicitly:

```bash
poetry run python -m scripts.migrate_database
mysql --host 127.0.0.1 --port 3306 --user YOUR_MYSQL_USER --password=YOUR_MYSQL_PASSWORD --database fastapi_admin < assets/sql/fastapi-admin.sql
```

After startup, open:

- API service: `http://127.0.0.1:3000`
- Swagger docs: `http://127.0.0.1:3000/docs`
- ReDoc docs: `http://127.0.0.1:3000/redoc`
- OpenAPI JSON: `http://127.0.0.1:3000/openapi.json`

## Docker Deployment

### 1. Select the Docker environment

Copy and fill the matching environment file first. `--env-file` supplies Compose interpolation variables, while `APP_ENV_FILE` makes the application, migration, MySQL, and Redis containers load the same profile.

Development:

```bash
docker compose --env-file .env.development up -d --build
```

Staging:

```bash
docker compose --env-file .env.staging up -d --build
```

Production: prepare `certs/fullchain.pem` and `certs/privkey.pem`, then enable the `fastapi-edge` profile:

```bash
docker compose --env-file .env.production --profile production up -d --build
```

After the first deployment, load seed data after the migration service completes:

```bash
docker compose --env-file .env.development exec -T fastapi-mysql sh -c 'mysql -uroot -p"$MYSQL_ROOT_PASSWORD" fastapi_admin' < assets/sql/fastapi-admin.sql
```

Replace `.env.development` with the selected staging or production file. Do not use development settings or `--watch` in production.

### 2. View logs

```bash
docker compose logs -f fastapi-app
```

### 3. Stop services

```bash
docker compose down
```

Default port mapping:


| Service | Container Port | Host Port |
| ------- | -------------- | --------- |
| FastAPI | 3000           | 127.0.0.1:3000 |
| MySQL   | 3306           | 127.0.0.1:3306 |
| Redis   | 6379           | 127.0.0.1:6379 |
| Nginx (production profile) | 80/443 | 80/443 |

The base Compose profile binds FastAPI, MySQL, and Redis to localhost. The production profile exposes only Nginx on ports 80/443 and proxies HTTPS traffic to FastAPI. Before staging or production deployment, copy the matching `.env.*.example`, replace every placeholder, prepare TLS certificates, and start Compose with `--env-file` pointing to the resulting file.

## API Modules


| Module       | Route Prefix | Description                                                         |
| ------------ | ------------ | ------------------------------------------------------------------- |
| User         | `/api/v1/user`      | User creation, login, self-service password change, administrator password reset, user info |
| Role         | `/api/v1/role`      | Role creation, list, detail, update, delete                         |
| Menu         | `/api/v1/menu`      | Menu creation, tree/list query, detail, update, delete               |
| Department   | `/api/v1/dept`      | Department tree query, create, update, delete                        |
| Post         | `/api/v1/post`      | Post list, create, update, delete                                     |
| Dictionary   | `/api/v1/dict`      | Dictionary type and dictionary data CRUD                              |
| Logs         | `/api/v1/log`       | Login, operation, exception log query and deletion                    |
| Online Users | `/api/v1/online`    | Online session query and forced logout                                |
| Captcha      | `/api/v1/captcha`   | Image captcha/verification; the plaintext numeric endpoint returns `410` |
| Health       | `/api/v1/health`    | Liveness and MySQL/Redis readiness probes                         |
| Metrics      | `/metrics`   | Prometheus request count, status, and latency metrics              |
| File Storage | `/api/v1/file`      | Local or Aliyun OSS upload, download, and deletion                 |
| System Config| `/api/v1/config`    | Key/value system parameters                                        |
| Notices      | `/api/v1/notice`    | Announcement CRUD                                                  |
| Jobs         | `/api/v1/job`       | Cron job management, manual run, and execution logs               |
| External Auth| `/api/v1/auth`      | OIDC/OAuth and LDAP login                                          |
| Backups      | `/api/v1/ops/backup`| Permission-protected database backup operations                    |
| Static Files | `/static`    | Static file access                                                  |

Use Swagger docs as the source of truth for full request and response schemas.

`GET /api/v1/captcha/image` returns a `captcha_id` and a Base64 image. Username login, phone login, and `GET /api/v1/captcha/verify` must submit both the `captcha_id` and the code shown in the image. The ID is bound to the client IP and is consumed after a successful verification. It is also deleted after `CAPTCHA_MAX_VERIFY_ATTEMPTS` failures, and expires after `CAPTCHA_TTL_SECONDS`.

## Authentication

Login APIs return a JWT token. For protected APIs, send it in the request header:

```http
Authorization: Bearer <access_token>
```

The token is signed with the `HS256` algorithm. Expiration is controlled by `ACCESS_TOKEN_EXPIRE_MINUTES`. After successful login, the token is cached in both process memory and Redis. The Redis key format is `auth:token:{sha256(token)}`.

Protected APIs check the in-memory cache first and then Redis. If both caches miss, the API returns `401 Token Not Found`. After a cache hit, the service still validates the JWT signature, expiration, and user status. The Redis TTL follows the token expiration time.

## Permissions and Response Models

- Routes use `Depends(Auth.has_permission("permission:code"))` for button-level authorization, for example `system:menu:edit`.
- The `permissions` table is the permission catalog. Button menus with `menu_type = F` connect `menu.perms` to `permissions.code`.
- Creating or updating a button menu syncs the permission catalog. Deleting a button menu removes the permission only when the same code is not used by other button menus.
- Roles connect to menus and button permissions through `role_menu`; authorization checks the user's roles, menu buttons, and permission catalog together.
- The super-admin wildcard `*:*:*` is stored in `permissions`, not returned as a menu. Users with the wildcard permission only need `*:*:*` in the returned permission list.
- `PUT /api/v1/user/{user_id}/password` is the self-service change-password endpoint and requires the old password. `PUT /api/v1/user/{user_id}/reset-password` is the administrator reset endpoint, uses `system:user:resetPwd`, and revokes the target user's active sessions after success.
- Login checks user status before issuing a token. A disabled user receives `用户已停用` and never receives a usable token.
- Validation failures keep structured `422` details under `data.errors`; clients should not parse a stringified exception.
- MySQL URLs are assembled with SQLAlchemy `URL.create()`, so usernames and passwords containing `@`, `:`, or `/` do not need manual escaping.
- Data scope is role-based and uses the union of all enabled roles assigned to the actor. Scope values are `1` all data, `2` selected departments, `3` current department, `4` current department and descendants, and `5` self only.
- `role_dept` stores selected departments for scope `2`. The service applies scope predicates to user, department, post, log, and online-session queries, and checks the same scope before detail, mutation, deletion, and forced logout operations.
- Role and menu configuration remains global system configuration. Changing a role's menus or data scope is restricted to super administrators; non-admin writes cannot use data scope as an escalation path.
- Runtime API responses are wrapped as `{ "code": 200, "message": "success", "data": ... }`. Unexpected failures return a sanitized 500 response while full tracebacks remain in server logs. Swagger uses `ApiResponseDto[T]` per route so response bodies show concrete schemas instead of `Any`.

## Common Commands

```bash
# Install dependencies
poetry install

# Apply schema migrations
poetry run python -m scripts.migrate_database

# Start development server
poetry run uvicorn main:app --host 0.0.0.0 --port 3000 --reload

# Run tests
poetry run python -m pytest -q

# Run unit tests and enforce the 60% coverage threshold
poetry run python -m pytest -q -m "not integration" --cov --cov-report=term-missing

# Start the local real MySQL/Redis services. Tests use randomized temporary rows
# and clean them up after each test.
docker compose up -d fastapi-mysql fastapi-redis
poetry run python -m scripts.migrate_database

# Run MySQL/Redis integration tests
RUN_INTEGRATION_TESTS=1 poetry run python -m pytest -q -m integration

# Run the real admin API tests without mocked services
RUN_INTEGRATION_TESTS=1 poetry run python -m pytest -q test/test_admin_api_async.py

# Verify an online migration downgrade followed by a fresh upgrade
poetry run alembic downgrade base
poetry run python -m scripts.migrate_database

# Verify encrypted backup, backup structure, and isolated restore rehearsal
poetry run python -m scripts.backup_database backup
poetry run python -m scripts.backup_database verify <filename>
poetry run python -m scripts.backup_database rehearse <filename>

# Create an isolated application for tests or multiple instances
from main import create_app
application = create_app()

# Register scheduled task handlers explicitly; task_name in /api/v1/job must match.
application = create_app(job_tasks={"example.task": lambda args: "ok"})

# Format code
poetry run black .
poetry run isort .

# Lint code
poetry run flake8 .

# Install pre-commit hooks
poetry run pre-commit install

# Commit with Commitizen
poetry run cz commit
```

## Coding Guidelines

- Follow the `Controller -> Service -> DAO -> Database` layering.
- Keep route handlers thin and move business logic into `service`.
- Keep database access inside `dao`.
- Use Pydantic for request and response schemas.
- Use SQLModel for database table models.
- Prefer `async/await` for async operations.
- Use Chinese docstrings for classes, functional methods, and important helpers; describe responsibilities and important side effects.
- Use Chinese inline comments for configuration constants, permission codes, cache keys, and lifecycle state.
- Use `Field(title=..., description=...)` for API fields, `description` for request parameters, and Chinese route `summary` values.
- Explain design reasons and cross-module constraints instead of restating obvious code. Update README, OpenAPI metadata, and test notes when behavior changes.
- Use Conventional Commits:

```text
feat: add user login
fix: handle redis timeout
refactor: simplify role service
docs: update readme
test: add user service tests
chore: update dependencies
```

## Seed Data

`assets/sql/fastapi-admin.sql` is a deployment-time seed script for initial users, roles, menus, permission catalog records, and role-menu relations. It is no longer executed from the application lifespan, which keeps startup read-only with respect to schema and seed data. The script uses `INSERT IGNORE`, so it can be rerun without duplicating existing primary-key records.

## FAQ

### 1. Missing environment variables on local startup

Make sure all required MySQL, Redis, and OSS variables are available in the process environment. Set `APP_ENV` to `development`, `staging`, or `production`; direct `uvicorn` startup can use the matching `.env.<APP_ENV>` file or process environment injection. Docker Compose should be started with `--env-file` pointing to the selected profile.

### 2. MySQL connection failed

Check:

- `MYSQL_HOST` and `MYSQL_POST`.
- Whether the database already exists.
- Username and password.
- Whether the MySQL container/service is running.

### 3. Redis authentication failed

Check:

- Whether `REDIS_PASSWORD` matches the Redis service.
- Whether Redis requires username authentication.
- Whether an empty `REDIS_USERNAME` matches your Redis configuration.

### 4. API returns 401

Make sure the request contains a valid token:

```http
Authorization: Bearer <access_token>
```

If the header is correct but the API still returns 401, also check:

- Whether the token still exists in memory or Redis.
- Whether Redis is reachable and `auth:token:` cache entries were not cleared.
- Whether `SECRET_KEY` stayed the same across restarts.
- Whether the token exceeded `ACCESS_TOKEN_EXPIRE_MINUTES`.

### 5. Requests are rate-limited

The default per-IP limit is `300/minute`, which permits concurrent admin-page requests. Username and phone login endpoints use `10/minute`, while captcha creation and verification use `30/minute`. Refresh-token, password-recovery, and external-auth endpoints have independent limits controlled by `RATE_LIMIT_REFRESH_TOKEN`, `RATE_LIMIT_PASSWORD_RESET`, and `RATE_LIMIT_EXTERNAL_AUTH`.

When one IP reaches `LOGIN_MAX_FAILED_ATTEMPTS` consecutive password failures within `LOGIN_IP_LOCK_SECONDS`, both username and phone login are blocked for `LOGIN_IP_LOCK_SECONDS`. The defaults are five failures and a 300-second lock. A correct password clears a failure counter that has not yet triggered a lock.

## Security and Operations

### Authentication and password policy

- Successful login returns a short-lived `access_token` and a rotating `refresh_token`. `POST /api/v1/user/token/refresh` consumes the old refresh token; reuse revokes the whole token family.
- Disabled users are rejected before token issuance. Protected routes also re-check user status, password version, and forced-password-change state.
- TOTP MFA is available through `POST /api/v1/user/mfa/setup`, `/api/v1/user/mfa/enable`, and `/api/v1/user/mfa/disable`. Login forms accept `mfa_code` or a one-time recovery code.
- `PASSWORD_*` settings control minimum length, character classes, password history, maximum age, and first-login password changes.
- Failed-login locking supports both IP and account dimensions through `LOGIN_MAX_FAILED_ATTEMPTS`, `LOGIN_IP_LOCK_SECONDS`, `LOGIN_ACCOUNT_MAX_FAILED_ATTEMPTS`, and `LOGIN_ACCOUNT_LOCK_SECONDS`.
- `POST /api/v1/user/password/forgot` and `/api/v1/user/password/reset` support email or SMS password recovery. Production must configure SMTP or an SMS webhook; recovery tokens are never returned in the response.
- Optional OIDC/OAuth and LDAP login use `/api/v1/auth/oidc/start`, `/api/v1/auth/oidc/callback`, and `/api/v1/auth/ldap/login` when the corresponding `OIDC_*` or `LDAP_*` settings are configured. OIDC requires `OIDC_ISSUER`, `OIDC_AUDIENCE`, and `OIDC_JWKS_URL`; callbacks validate the signature, issuer, audience, nonce, PKCE, and `email_verified`, and external login still requires an MFA code.

### Tenants and permissions

- Users, roles, menus, departments, posts, dictionaries, notices, files, jobs, configs, and logs carry `tenant_id`; reads and writes are filtered by the current tenant.
- Tenant members can switch tenant context through `/api/v1/tenant/switch`; missing tenant context fails closed for protected business queries.
- Mutating requests may send `Idempotency-Key`; batch user and role changes write before/after snapshots and request transactions roll back on failure.
- Startup synchronizes routes using `Auth.has_permission(...)` into `api_permission_catalog`.
- Field permissions use `field:<resource>:<field>` and are bound through the role DTO's `field_permission_codes`. Sensitive user fields are hidden when the actor lacks the field permission.
- Role and menu permission changes are recorded in `permission_change_versions` with actor, version, and before/after snapshots.

### Files, notices, and operations

- Files support signature detection, optional ClamAV scanning, OSS presigned URLs, local/OSS storage, chunked upload, and text redaction.
- When `FILE_VIRUS_SCAN_ENABLED=true`, provide a reachable ClamAV service and configure `CLAMAV_HOST`/`CLAMAV_PORT`; the default Compose file does not include a ClamAV container.
- The chunked upload flow is `POST /api/v1/file/chunk/init`, `PUT /api/v1/file/chunk/{upload_id}/{chunk_index}`, then `POST /api/v1/file/chunk/complete`. Incomplete chunk records and temporary directories are periodically removed according to `FILE_CHUNK_TTL_SECONDS`.
- System-config values of type `secret`, `password`, or `sensitive` are encrypted at rest and returned as a mask in list, detail, and value responses. Do not log sensitive values or commit them to environment examples.
- Text redaction is exposed through `GET /api/v1/file/redacted/{file_id}` and requires `FILE_REDACTION_ENABLED=true`.
- Users, roles, and dictionaries support Excel import/export. Imports still apply DTO validation, password policy, tenant checks, and duplicate checks.
- Users, roles, and dictionaries also support persistent asynchronous exports: call `/export/async`, poll `/export/tasks/{task_id}`, and download from `/export/tasks/{task_id}/download` after completion.
- Notices support recipients, inbox queries, unread filtering, and read state through `GET /api/v1/notice/inbox/list` and `POST /api/v1/notice/{notice_id}/read`.
- Notices support inbox, webhook, email, and SMS delivery. External delivery failures use a database-backed lease plus bounded exponential backoff using `NOTIFICATION_DELIVERY_LEASE_SECONDS`, `NOTIFICATION_RETRY_MAX_ATTEMPTS`, and `NOTIFICATION_RETRY_BASE_SECONDS`.
- Database backups can be created with `poetry run python -m scripts.backup_database backup` or the platform-super-admin-protected `/api/v1/ops/backup/create` endpoint. Run `poetry run python -m scripts.backup_database verify <filename>` or `/api/v1/ops/backup/verify` before `poetry run python -m scripts.backup_database rehearse <filename>` or `/api/v1/ops/backup/rehearse`; rehearsal imports into `BACKUP_REHEARSAL_DATABASE` and removes it afterward. Online restore is disabled by default and requires an explicit maintenance window, operations token, and MFA reauthentication. Backups are Fernet-encrypted and cleaned up according to the retention policy.

### Jobs and observability

- APScheduler triggers jobs. With `SCHEDULER_WORKER_MODE=queue`, jobs are published to Redis Streams and executed by the independent `fastapi-worker` service. The Worker exposes a heartbeat, claims idle messages, and renews the task lock during long execution.
- A Redis `SET NX EX` lock prevents duplicate execution across instances. Jobs support timeout, retry, pause/resume, and execution logs.
- `SCHEDULER_DEFAULT_TIMEOUT_SECONDS`, `SCHEDULER_LOCK_TTL_SECONDS`, and `SCHEDULER_DEFAULT_MAX_RETRIES` define defaults; individual job DTOs can override timeout and retries.
- `/metrics` exposes HTTP metrics plus MySQL/Redis readiness, job executions/durations, and alert delivery state. Configure `ALERT_WEBHOOK_URL` to send structured job-failure alerts.
- Set `OTEL_ENABLED=true` and `OTEL_EXPORTER_OTLP_ENDPOINT` to export FastAPI traces over OTLP. Log files are retained according to `LOG_RETENTION_DAYS`. Outside development, `/docs`, `/redoc`, `/openapi.json`, and `/metrics` require `DOCS_AUTH_TOKEN` or `METRICS_AUTH_TOKEN`.

### Migrations and Docker troubleshooting

The current migration head is `0025_security_consistency`. The migration entrypoint creates or expands `alembic_version.version_num` to `VARCHAR(64)`, which handles older databases created with Alembic's default `VARCHAR(32)`. Check that `/api/v1/health/ready` reports `schema=ok` after deployment.

```bash
docker compose --env-file .env.development up -d --build
docker compose --env-file .env.development logs -f fastapi-migrate
poetry run python -m scripts.migrate_database
```

An `1045 Access denied` error means the credentials in the persistent MySQL volume differ from the selected environment file. A volume does not rotate passwords when `.env` changes: preserve data by rotating `fastapi_app` with the original root password; only use `docker compose down -v` for disposable development data. Never delete a production volume to resolve `1045`.

## License

No license is declared in this repository yet. Add one before public release or commercial use.
