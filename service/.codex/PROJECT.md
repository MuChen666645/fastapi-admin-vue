# FastAPI Admin Vue Service 项目说明

## 项目定位

这是一个以 FastAPI 为核心的后台管理服务，负责用户、角色、菜单、部门、岗位、字典、日志、文件、通知、定时任务、租户和系统配置等管理能力。

当前仓库是后端优先阶段，尚未正式接入前端。管理 API 只保留版本化前缀 `/api/v1`，不要为了兼容未上线的前端新增无前缀旧接口。

项目根目录为当前仓库目录，应用入口是 `main.py`，ASGI 对象为 `main:app`，默认监听端口为 `3000`。

## 信息权威和适用范围

遇到冲突时按以下顺序判断：

1. 系统、开发者和用户本轮明确要求。
2. 当前工作区中的源代码、配置、迁移和测试。
3. 本目录中的 Codex 约束文件。
4. README、历史记录、旧 issue 和过往运行摘要。

本目录是当前项目的工作规范，不是业务合同本身。任何文档与当前代码或测试冲突时，应先以当前代码为准，修正文档，并在实现报告中说明差异；不能根据旧文档臆造不存在的接口、字段或运行能力。

## 技术栈

- Python 3.11+
- FastAPI + Uvicorn
- Pydantic Settings + Pydantic DTO
- SQLModel + SQLAlchemy AsyncSession + aiomysql
- MySQL 8.x
- Redis 7.x（Token、验证码、限流、幂等、任务队列和锁）
- PyJWT、passlib、cryptography
- Alembic
- fastapi-pagination
- SlowAPI
- Loguru、Prometheus、OpenTelemetry
- Pillow、openpyxl、oss2
- APScheduler 和可选的独立 Worker
- Poetry、Docker Compose、Nginx

## 目录职责

```text
main.py                 应用工厂、生命周期、中间件、运维入口
config/                 环境配置、MySQL、Redis、限流
module_admin/
  auth/                 JWT、Token 缓存、认证、权限依赖
  controller/            API 路由和请求依赖
  service/               业务编排、异步任务和跨模块规则
  dao/                   数据库查询、持久化、租户和数据范围过滤
  entity/do/             SQLModel 数据库模型
  entity/dto/            Pydantic 请求、响应和分页 DTO
middleware/             请求关联、日志、响应、幂等、观测中间件
interceptors/            异常和错误响应处理
alembic/                 数据库版本迁移
assets/sql/              初始化和历史升级 SQL 资源
scripts/                 迁移、备份、独立任务 Worker 入口
test/                    单元、API、回归和 Docker 集成测试
deploy/                  生产 Nginx 配置
static/                  应用静态资源
.codex/                  本项目的 Codex 工作约束和提示模板
```

文件名 `menu_contorller.py` 是现有项目名称，修改菜单模块时沿用该路径，不要为了纠正拼写进行无关重命名。

## API 约定

- `module_admin/controller` 中的 `APIRouter` 只定义模块局部前缀，例如 `/user`、`/role`、`/health`。
- `module_admin/v1.py` 统一以 `settings.API_V1_PREFIX` 注册全部管理路由，默认值为 `/api/v1`。
- 正式业务接口示例：`/api/v1/user/login/username`、`/api/v1/user/list`、`/api/v1/health/ready`。
- 应用级入口不属于管理 API 版本组：`/docs`、`/redoc`、`/openapi.json`、`/metrics`、`/static/*`。
- JSON 响应通常由 `ResponseInterceptor` 包装为 `code`、`message`、`data`；需要返回文件、流、HTML 或原始 JSON 时，使用现有的跳过包装机制。
- API 字段和参数名必须与 DTO 保持一致。模型字段使用 `Field(title=...)`，查询、路径和文件参数使用 `description=...`，路由提供明确的 `summary`。
- 分页使用 `fastapi-pagination`，不要自行发明分页字段；以现有 `Page` 响应结构和测试断言为准。

## 运行配置

`config/env.py` 根据 `APP_ENV` 选择 `.env.development`、`.env.staging` 或 `.env.production`。环境变量优先级高于环境文件。`APP_ENV_FILE` 主要由 Docker Compose 用来选择容器的 `env_file`，不等同于直接运行 Uvicorn 时的配置选择器。

配置大致分为：

- FastAPI：`DEBUG`、`TITLE`、`SUMMARY`、`VERSION`、`OPENAPI_URL`、`API_V1_PREFIX`
- MySQL/Redis：主机、端口、账号、密码、数据库名和时区
- 认证安全：`SECRET_KEY`、Token 生命周期、密码策略、MFA、登录失败锁定
- RBAC/租户：`ADMIN_ROLE_CODE`、`DEFAULT_TENANT_ID` 和权限相关开关
- 限流/验证码：登录、验证码、刷新 Token、密码找回和外部认证的限流及 TTL
- 文件/OSS：本地目录、大小、扩展名、内容探测、ClamAV、OSS 和分片上传
- 调度/任务：`SCHEDULER_*`、`EXPORT_*`、`WORKER_*`、Redis Stream 和任务锁
- 观测/运维：OpenTelemetry、日志保留、告警、文档 Token、指标 Token

生产和 staging 必须使用真实生成的密钥、关闭 Debug、限制 `HOSTS`/`ORIGINS`/`HEADERS`，配置 Redis 密码，并配置文档和指标访问 Token。文档、示例和提示词中只能使用占位符，不得写入真实密钥。

## 常用命令

在 Windows 本地测试时，先覆盖可能继承的环境变量：

```powershell
$env:APP_ENV = "development"
$env:DEBUG = "true"
poetry run python -m pytest -q
```

常用开发命令：

```bash
poetry install
poetry run uvicorn main:app --host 0.0.0.0 --port 3000 --reload
poetry run python -m scripts.migrate_database
poetry run python -m pytest -q -m "not integration"
RUN_INTEGRATION_TESTS=1 poetry run python -m pytest -q -m integration
poetry run python -m compileall -q main.py module_admin config middleware interceptors scripts alembic test
poetry run black --check path/to/changed_file.py
poetry run isort --check-only --profile black .
poetry run flake8 --max-line-length=88 .
```

集成测试需要可用的 MySQL 和 Redis。仅完成测试收集不代表集成测试已经执行；必须单独记录 Docker/外部依赖是否真正可用。

## 当前状态和非目标

- 当前没有前端代码和前端联调合同，不要虚构 Vue 路由、前端 payload 或页面行为。
- 管理接口已经取消旧无前缀路由兼容，不要重新添加 `API_LEGACY_ENABLED` 或第二次 `include_router`。
- 数据库 schema 变更应通过 Alembic 迁移完成，并在启动前由 `fastapi-migrate` 或迁移脚本执行。
- 备份、生产运维、OSS 和真实 Docker 依赖的验证结果必须区分于本地单元测试结果。
- 不做与任务无关的全项目重构、依赖升级、文件重命名或生成物清理。
