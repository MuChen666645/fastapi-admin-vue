# FastAPI Admin Vue

> 企业级多租户管理平台，基于 Vue 3 管理端与 FastAPI 服务构建。

[English](./README.en.md) | [开发文档](./DEVELOPMENT.md) | [仓库规范](./.codex/README.md)

## 概览

FastAPI Admin Vue 是一个前后端分离的企业管理平台。`frontend/` 提供基于 Vue 3 的管理工作台，
`service/` 提供基于 FastAPI 的版本化管理 API、认证授权、租户隔离、业务规则和数据持久化。

平台面向内部运营系统、多租户后台和企业管理场景，遵循以下工程原则：

- **服务端权威**：认证、授权、租户、数据范围、业务状态和数据一致性由后端强制保证。
- **契约驱动**：前端通过类型化 API、Parser 和统一请求层调用已核验的 `/api/v1` 接口。
- **职责清晰**：前端页面、Store、API 和布局分层；后端 Controller、Service、DAO 和数据库分层。
- **可验证交付**：变更通过聚焦测试、静态检查、构建、离线迁移 SQL 和必要的真实依赖验证逐层确认。

## 核心能力

| 领域       | 能力                                                                   |
| ---------- | ---------------------------------------------------------------------- |
| 身份与会话 | 登录、验证码、Token 刷新、密码策略、强制改密、MFA 与会话撤销           |
| 权限与组织 | 用户、角色、菜单、按钮权限、字段权限、部门、岗位与数据范围             |
| 多租户     | 租户生命周期、成员关系、租户切换、租户隔离与默认租户保护               |
| 系统管理   | 字典、系统参数、消息中心、文件、登录/操作/异常日志与在线会话           |
| 作业与运维 | Cron 任务、执行日志、异步导出、备份、健康检查、指标与链路追踪          |
| 管理端体验 | 服务端动态路由、权限可见性、标签页、缓存、主题、国际化、时区和 Loading |

页面和操作是否可用取决于后端下发的菜单、当前用户权限以及目标环境实际部署的能力。

## 架构

```text
Vue 页面 / BasicLayout / Store
  -> 领域 API 与响应 Parser
  -> 统一请求层
  -> HTTP /api/v1
  -> FastAPI Controller
  -> Auth / Tenant / Data Scope
  -> Service 业务规则与事务
  -> DAO / SQLModel
  -> MySQL / Redis / Worker / 外部服务
```

前端的菜单、按钮和路由守卫只用于改善体验，不能替代后端授权。服务端动态路由只允许映射到
前端本地视图白名单，未知组件路径不会被动态执行。

## 项目结构

```text
.
├── frontend/                 # Vue 3 管理端
│   ├── src/api/              # 领域 API、请求编码和响应 Parser
│   ├── src/layouts/          # BasicLayout、系统设置抽屉和应用壳层
│   ├── src/router/           # 静态路由、守卫和动态路由转换
│   ├── src/stores/           # 会话、偏好、字典、标签、消息和 Loading
│   └── src/__tests__/        # Vitest 行为与契约测试
├── service/                  # FastAPI 服务
│   ├── module_admin/         # Controller、Service、DAO、DO 和 DTO
│   ├── alembic/              # 版本化数据库迁移
│   ├── assets/sql/           # 初始化和升级 SQL
│   ├── scripts/              # 迁移、备份和 Worker 入口
│   └── test/                 # pytest 契约、安全和回归测试
├── .agents/skills/           # 跨前后端 Agent Skill
├── .codex/                   # 仓库级开发规范
└── DEVELOPMENT.md            # 开发协作说明
```

## 快速开始

### 运行要求

- Node.js：以 [frontend/package.json](./frontend/package.json) 的 `engines` 为准。
- pnpm：前端包管理器。
- Python 3.11+ 与 Poetry：后端运行与依赖管理。
- MySQL 8.x 与 Redis 6.x+：后端真实运行依赖。
- Docker Compose：本地容器化依赖和部署验证时需要。

### 1. 启动后端依赖和服务

```powershell
Set-Location service
Copy-Item .env.development.example .env.development

docker compose --env-file .env.development up -d fastapi-mysql fastapi-redis
poetry install
$env:APP_ENV = "development"
$env:DEBUG = "true"
poetry run python -m scripts.migrate_database
poetry run uvicorn main:app --host 0.0.0.0 --port 3000 --reload
```

服务默认地址为 `http://127.0.0.1:3000`。健康检查使用 `/api/v1/health/live` 与
`/api/v1/health/ready`；开发环境的 OpenAPI 文档位于 `/docs`。

### 2. 启动前端

```powershell
Set-Location ..\frontend
Copy-Item .env.example .env.local
pnpm install
pnpm run dev
```

前端默认地址为 `http://127.0.0.1:5173`。开发代理将 `/api` 转发到后端；`VITE_*` 值会进入
浏览器构建产物，不得配置密码、Token、密钥或内部凭据。

### 3. 使用 Docker Compose 启动完整后端栈

```powershell
Set-Location service
docker compose --env-file .env.development up -d --build
```

该流程会等待 MySQL/Redis 健康检查及迁移服务成功后再启动应用与 Worker。生产部署前必须完成
密钥注入、Host/CORS 收敛、TLS、备份和就绪探针验证。

## 前后端契约

管理 API 使用后端 `API_V1_PREFIX`，当前为 `/api/v1`。常规 JSON 成功响应遵循：

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

文件、流和明确要求原始响应的接口不使用 JSON 包装。完整字段、分页、状态码、权限和错误语义以当前
后端 OpenAPI、DTO、Controller 与测试为准，不能根据 README 推测。

新增或变更接口时必须同步核对：

1. 方法、完整路径、Path/Query/Body/FormData、分页和排序。
2. 成功响应、空值、错误、文件/流和响应包装。
3. 登录态、权限码、租户、数据范围、资源所有权、幂等、重试与回滚。
4. 后端 DTO/Controller/Service/DAO/测试，以及前端类型/API/Parser/调用方/测试。

## 开发与质量

常用验证命令：

```powershell
# 前端
Set-Location frontend
pnpm run check
pnpm run test:run
pnpm run build

# 后端
Set-Location ..\service
$env:APP_ENV = "development"
$env:DEBUG = "true"
poetry run python -m pytest -q
poetry run python -m compileall -q main.py module_admin config middleware interceptors scripts alembic test
poetry run alembic upgrade head --sql

# 仓库根目录
git diff --check
```

先运行与变更最接近的测试；涉及请求层、认证、动态路由、共享布局、迁移、构建或运行配置时，再扩大验证范围。
单元测试、静态检查和离线 SQL 不代表 MySQL、Redis、Docker、浏览器、OIDC/LDAP/SMTP、OSS 或生产环境已经验证。

## 数据库与后台任务

数据库结构由 Alembic 管理，当前迁移 head 为 `0028_tenant_and_system_parameter_menus`。已应用的
`service/alembic/versions/` 文件属于部署升级历史，不得删除、改名、压缩或重写；修复通过新增迁移完成。

定时任务仅在后端启用调度器且 `task_name` 已注册处理器时可执行。持久化作业记录不会自动创建任务处理器，
长耗时工作应使用 Scheduler、Worker 或异步导出，不得阻塞 HTTP 请求。

## 安全与发布边界

- 不提交真实密码、Token、密钥、验证码、MFA、生产数据、数据库备份、缓存、覆盖率和构建产物。
- 后端负责最终认证、授权、租户、数据范围和资源所有权校验；前端隐藏操作不是安全边界。
- 数据库迁移、备份恢复、Redis 清理、Docker、外部身份、OSS、SMTP、Webhook 和生产操作需确认环境、目标、权限与数据影响。
- 未经明确要求，不提交、推送、创建 PR 或操作远程资源。

## 文档与 Agent Skill

| 主题               | 入口                                                                                              |
| ------------------ | ------------------------------------------------------------------------------------------------- |
| 仓库开发与联动规范 | [DEVELOPMENT.md](./DEVELOPMENT.md)、[.codex/README.md](./.codex/README.md)                        |
| 前端说明           | [frontend/README.md](./frontend/README.md) · [English](./frontend/README.en.md)                   |
| 后端说明           | [service/README.md](./service/README.md) · [English](./service/README.en.md)                      |
| 跨端契约变更       | [.agents/skills/fullstack-contract-change](./.agents/skills/fullstack-contract-change/SKILL.md)   |
| 跨端功能交付       | [.agents/skills/fullstack-feature-delivery](./.agents/skills/fullstack-feature-delivery/SKILL.md) |
| 联动验证           | [.agents/skills/fullstack-validation](./.agents/skills/fullstack-validation/SKILL.md)             |
| 仓库评审           | [.agents/skills/repository-code-review](./.agents/skills/repository-code-review/SKILL.md)         |

## 许可证

仓库当前未声明许可证。对外分发或商业交付前，应补充适用许可证、第三方依赖合规说明和发布策略。
