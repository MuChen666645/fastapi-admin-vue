# FastAPI Admin Vue Service

> 中文 | [English](#english)

FastAPI Admin Vue Service 是一个基于 **FastAPI + SQLModel + MySQL + Redis** 的后台管理系统服务端工程。项目采用分层结构组织业务代码，包含用户、角色、菜单、验证码、JWT 鉴权、按钮级权限控制、统一响应拦截、请求日志、限流、静态资源和 Docker 部署配置。

## 功能特性

- FastAPI 异步 Web API 服务
- SQLModel + SQLAlchemy AsyncSession 数据访问
- MySQL 数据持久化
- Redis 缓存、验证码存储与 Token 二级缓存
- JWT 登录认证、Token 内存/Redis 校验与按钮级接口权限校验
- 用户、角色、菜单管理模块，菜单按钮权限同步到权限目录
- 若依风格 RBAC 权限模型，支持超级管理员通配权限 `*:*:*`
- 图片验证码生成与校验；明文数字验证码接口已停用
- 统一响应拦截与异常处理
- 请求日志中间件
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

## 环境要求

- Python 3.11+
- Poetry 1.8+
- MySQL 8.x
- Redis 6.x+
- Docker / Docker Compose，可选

## 环境变量

项目运行依赖以下环境变量。Docker Compose 会读取当前目录下的 `.env` 文件；如果直接使用 `uvicorn` 启动，请确保这些变量已经注入到当前进程环境中。

```env
# MySQL
MYSQL_HOST=127.0.0.1
MYSQL_POST=3306
MYSQL_USERNAME=root
MYSQL_PASSWORD=your_mysql_password
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

# Optional
SECRET_KEY=replace_with_a_stable_random_secret
ACCESS_TOKEN_EXPIRE_MINUTES=3600
RATE_LIMIT_DEFAULT=300/minute
RATE_LIMIT_LOGIN=10/minute
RATE_LIMIT_CAPTCHA=30/minute
CAPTCHA_TTL_SECONDS=300
CAPTCHA_MAX_VERIFY_ATTEMPTS=5
LOGIN_MAX_FAILED_ATTEMPTS=5
LOGIN_IP_LOCK_SECONDS=300
HOSTS=["*"]
ORIGINS=["*"]
MEDOTHS=["*"]
HEADERS=["*"]
CREDENTIALS=false
```

> 注意：`MYSQL_POST`、`REDIS_POST`、`MEDOTHS`、`ACCESSKEY_SECRET` 是当前代码中的实际配置项名称，请保持一致。

> `SECRET_KEY` 代码内提供了稳定默认值，避免服务重启后因随机密钥变化导致已签发 Token 全部失效。生产环境仍建议通过环境变量配置高强度固定密钥，并妥善保存。

## 本地开发

### 1. 安装依赖

```bash
poetry install
```

### 2. 准备 MySQL 与 Redis

可以使用本机服务，也可以通过 Docker Compose 只启动依赖服务：

```bash
docker compose up -d fastapi-mysql fastapi-redis
```

### 3. 创建数据库

如果没有使用 `docker-compose.yml` 中的默认数据库，请手动创建数据库：

```sql
CREATE DATABASE fastapi_admin DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

服务启动时会通过 SQLModel 初始化数据表，并执行 `assets/sql/fastapi-admin.sql` 中的初始数据脚本。

### 4. 启动服务

```bash
poetry run uvicorn main:app --host 0.0.0.0 --port 3000 --reload
```

启动成功后访问：

- API 服务：`http://127.0.0.1:3000`
- Swagger 文档：`http://127.0.0.1:3000/docs`
- ReDoc 文档：`http://127.0.0.1:3000/redoc`
- OpenAPI JSON：`http://127.0.0.1:3000/openapi.json`

## Docker 部署

### 构建并启动全部服务

```bash
docker compose up --build --watch
```

### 查看日志

```bash
docker compose logs -f fastapi-app
```

### 停止服务

```bash
docker compose down
```

默认端口映射：


| 服务    | 容器端口 | 本机端口 |
| ------- | -------- | -------- |
| FastAPI | 3000     | 3000     |
| MySQL   | 3306     | 3306     |
| Redis   | 6379     | 6379     |

生产环境部署前请修改默认数据库密码、Redis 密码、JWT `SECRET_KEY`，并限制 `HOSTS` 与 CORS 来源。

## API 模块


| 模块     | 路由前缀   | 说明                                                     |
| -------- | ---------- | -------------------------------------------------------- |
| 用户     | `/user`    | 用户创建、用户名登录、手机号密码登录、当前/指定用户信息查询 |
| 角色     | `/role`    | 角色创建、列表查询、详情、更新、删除                     |
| 菜单     | `/menu`    | 菜单创建、菜单树/列表查询、详情、更新、删除              |
| 验证码   | `/captcha` | 图片验证码与校验；明文数字验证码接口返回 `410`           |
| 静态资源 | `/static`  | 静态文件访问                                             |

完整请求参数与响应结构请以 Swagger 文档为准。

`GET /captcha/image` 返回 `captcha_id` 和 Base64 图片。用户名登录、手机号登录及 `GET /captcha/verify` 必须同时提交 `captcha_id` 与图片中的验证码。验证码 ID 绑定获取时的客户端 IP，校验成功后立即失效；连续错误达到 `CAPTCHA_MAX_VERIFY_ATTEMPTS` 次后也会失效，有效期由 `CAPTCHA_TTL_SECONDS` 控制。

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
- 接口运行时统一返回 `{ "code": 200, "message": "success", "data": ... }`。Swagger 中每个接口使用 `ApiResponseDto[T]` 描述实际响应体，避免响应体展示为 `Any`。

## 常用命令

```bash
# 安装依赖
poetry install

# 启动开发服务
poetry run uvicorn main:app --host 0.0.0.0 --port 3000 --reload

# 运行测试
poetry run pytest

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

`assets/sql/fastapi-admin.sql` 会在服务启动生命周期中执行，用于写入初始用户、角色、菜单、权限目录和角色菜单关系等基础数据。脚本使用 `INSERT IGNORE`，重复启动时不会重复插入已有主键数据。

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

项目默认对每个 IP 限制 `300/minute`，允许后台页面并发加载；用户名和手机号登录限制为 `10/minute`，验证码获取及校验限制为 `30/minute`。可通过 `RATE_LIMIT_DEFAULT`、`RATE_LIMIT_LOGIN` 和 `RATE_LIMIT_CAPTCHA` 环境变量调整。

同一 IP 在 `LOGIN_IP_LOCK_SECONDS` 秒内连续输错密码达到 `LOGIN_MAX_FAILED_ATTEMPTS` 次后，将禁止用户名和手机号登录，锁定时间同为 `LOGIN_IP_LOCK_SECONDS` 秒。默认连续错误 5 次锁定 300 秒，密码校验正确会清除尚未触发锁定的失败计数。

## License

当前仓库未声明 License。请在发布或商用前补充许可证信息。

---

## English

> [中文](#fastapi-admin-vue-service) | English

FastAPI Admin Vue Service is a backend service for an admin management system built with **FastAPI, SQLModel, MySQL, and Redis**. It follows a layered architecture and includes user management, role management, menu management, captcha, JWT authentication, button-level authorization, response interception, request logging, rate limiting, static files, and Docker deployment support.

## Features

- Async FastAPI Web API service
- SQLModel + SQLAlchemy AsyncSession data access
- MySQL persistence
- Redis cache, captcha storage, and token cache
- JWT login authentication, memory/Redis token validation, and button-level route authorization
- User, role, and menu management modules with menu button permission synchronization
- RuoYi-style RBAC model with super-admin wildcard permission `*:*:*`
- Image captcha generation/verification; the plaintext numeric endpoint is disabled
- Unified response interception and exception handling
- Request logging middleware
- SlowAPI rate limiting
- Swagger/OpenAPI API documentation with concrete per-route response DTOs
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

## Requirements

- Python 3.11+
- Poetry 1.8+
- MySQL 8.x
- Redis 6.x+
- Docker / Docker Compose, optional

## Environment Variables

The service depends on the following environment variables. Docker Compose reads `.env` from the current directory. If you run the application directly with `uvicorn`, make sure these variables are available in the process environment.

```env
# MySQL
MYSQL_HOST=127.0.0.1
MYSQL_POST=3306
MYSQL_USERNAME=root
MYSQL_PASSWORD=your_mysql_password
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

# Optional
SECRET_KEY=replace_with_a_stable_random_secret
ACCESS_TOKEN_EXPIRE_MINUTES=3600
RATE_LIMIT_DEFAULT=300/minute
RATE_LIMIT_LOGIN=10/minute
RATE_LIMIT_CAPTCHA=30/minute
CAPTCHA_TTL_SECONDS=300
CAPTCHA_MAX_VERIFY_ATTEMPTS=5
LOGIN_MAX_FAILED_ATTEMPTS=5
LOGIN_IP_LOCK_SECONDS=300
HOSTS=["*"]
ORIGINS=["*"]
MEDOTHS=["*"]
HEADERS=["*"]
CREDENTIALS=false
```

> Note: `MYSQL_POST`, `REDIS_POST`, `MEDOTHS`, and `ACCESSKEY_SECRET` are the actual setting names used by the current codebase. Keep them unchanged unless the code is updated.

> The code provides a stable default `SECRET_KEY` so issued tokens are not invalidated by a random key after every restart. For production, still set a strong fixed key through environment variables and keep it safe.

## Local Development

### 1. Install dependencies

```bash
poetry install
```

### 2. Prepare MySQL and Redis

You can use local services or start only the dependency services with Docker Compose:

```bash
docker compose up -d fastapi-mysql fastapi-redis
```

### 3. Create the database

If you are not using the default database from `docker-compose.yml`, create it manually:

```sql
CREATE DATABASE fastapi_admin DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

During startup, the service initializes tables through SQLModel and executes the seed script at `assets/sql/fastapi-admin.sql`.

### 4. Start the service

```bash
poetry run uvicorn main:app --host 0.0.0.0 --port 3000 --reload
```

After startup, open:

- API service: `http://127.0.0.1:3000`
- Swagger docs: `http://127.0.0.1:3000/docs`
- ReDoc docs: `http://127.0.0.1:3000/redoc`
- OpenAPI JSON: `http://127.0.0.1:3000/openapi.json`

## Docker Deployment

### Build and start all services

```bash
docker compose up -d --build
```

### View logs

```bash
docker compose logs -f fastapi-app
```

### Stop services

```bash
docker compose down
```

Default port mapping:


| Service | Container Port | Host Port |
| ------- | -------------- | --------- |
| FastAPI | 3000           | 3000      |
| MySQL   | 3306           | 3306      |
| Redis   | 6379           | 6379      |

Before production deployment, change the default MySQL password, Redis password, JWT `SECRET_KEY`, and restrict `HOSTS` and CORS origins.

## API Modules


| Module       | Route Prefix | Description                                                         |
| ------------ | ------------ | ------------------------------------------------------------------- |
| User         | `/user`      | User creation, username login, phone/password login, current/target user info |
| Role         | `/role`      | Role creation, list, detail, update, delete                         |
| Menu         | `/menu`      | Menu creation, tree/list query, detail, update, delete               |
| Captcha      | `/captcha`   | Image captcha/verification; the plaintext numeric endpoint returns `410` |
| Static Files | `/static`    | Static file access                                                  |

Use Swagger docs as the source of truth for full request and response schemas.

`GET /captcha/image` returns a `captcha_id` and a Base64 image. Username login, phone login, and `GET /captcha/verify` must submit both the `captcha_id` and the code shown in the image. The ID is bound to the client IP and is consumed after a successful verification. It is also deleted after `CAPTCHA_MAX_VERIFY_ATTEMPTS` failures, and expires after `CAPTCHA_TTL_SECONDS`.

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
- Runtime API responses are wrapped as `{ "code": 200, "message": "success", "data": ... }`. Swagger uses `ApiResponseDto[T]` per route so response bodies show concrete schemas instead of `Any`.

## Common Commands

```bash
# Install dependencies
poetry install

# Start development server
poetry run uvicorn main:app --host 0.0.0.0 --port 3000 --reload

# Run tests
poetry run pytest

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

`assets/sql/fastapi-admin.sql` is executed during the application lifespan startup hook to seed initial users, roles, menus, permission catalog records, and role-menu relations. It uses `INSERT IGNORE`, so repeated startups do not duplicate existing primary-key records.

## FAQ

### 1. Missing environment variables on local startup

Make sure all required MySQL, Redis, and OSS variables are available in the process environment. Docker Compose reads `.env` from the current directory. For direct `uvicorn` startup, verify the environment file path used by Pydantic based on your actual working directory, or use system environment variables.

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

The default per-IP limit is `300/minute`, which permits concurrent admin-page requests. Username and phone login endpoints use `10/minute`, while captcha creation and verification use `30/minute`. Override these values with `RATE_LIMIT_DEFAULT`, `RATE_LIMIT_LOGIN`, and `RATE_LIMIT_CAPTCHA`.

When one IP reaches `LOGIN_MAX_FAILED_ATTEMPTS` consecutive password failures within `LOGIN_IP_LOCK_SECONDS`, both username and phone login are blocked for `LOGIN_IP_LOCK_SECONDS`. The defaults are five failures and a 300-second lock. A correct password clears a failure counter that has not yet triggered a lock.

## License

No license is declared in this repository yet. Add one before public release or commercial use.
