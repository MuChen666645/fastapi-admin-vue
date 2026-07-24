# 后端 Codex 工作流

## 工作目标

每次任务都要从当前代码和测试得到结论，再修改最小必要范围。默认工作顺序是：理解上下文 → 明确边界 → 设计合同 → 增量实现 → 分层验证 → 汇报结果。不要只写计划后停止；如果用户要求改动，应完成实现和验证。

## 0. 操作模式和授权

- 解释、评审、审计和状态报告默认只读，不修改源代码、文档、数据库、远程 Git 或外部系统。
- 诊断请求先确定根因；只有用户同时要求修复，或请求明确包含“实现/修改/修复”时才写入代码。
- 实现请求只修改用户明确放入范围的仓库和文件；不因为“顺手整理”扩大到依赖升级、重命名、全量格式化或前端实现。
- 需要提交、推送、创建 PR、访问生产数据、调用真实第三方服务或执行破坏性命令时，先确认具体目标和授权。
- 评审任务如果没有明确 comparison target，先确认分支或比较基线，再读取 diff。

后端任务默认不修改 `frontend/`。如果任务改变 API 契约，先在变更记录中写出前端影响；只有用户明确要求联动时，才修改前端并同时执行前端类型检查或构建验证。

## 1. 任务开始

先执行只读检查：

```powershell
git status --short --branch
rg -n "目标符号|目标路径|相关配置" .
rg --files module_admin test config scripts
```

读取任务涉及的 Controller、Service、DAO、DTO/DO、配置、迁移和测试。先确认：

- 当前分支和工作区是否已有用户修改
- 实际路由是否为 `/api/v1/...`
- 请求是否有 MySQL 依赖、Redis 依赖、认证依赖和租户依赖
- 相关权限码是否已有 SQL seed
- 既有测试是单元测试还是需要真实 MySQL/Redis 的 integration 测试

若任务涉及前端调用，还要读取 `E:\fastapi-admin-vue\frontend\.codex\PROJECT.md`，并搜索 `frontend/src` 中实际存在的调用方、类型和页面，确认调用方没有依赖旧字段或旧响应结构。当前前端为基础模板，未找到调用方时不得臆造联调实现。

不要回滚或覆盖不属于本次任务的工作区修改。若目标文件已有用户改动，先逐段理解后再整合。

## 2. 先确定变更类型

### 接口或功能变更

先写清楚请求、响应、错误、权限、租户、数据范围、事务、幂等和失败行为。新增管理 API 必须放在 `module_admin/controller` 并通过 `AdminAPI` 注册到 `/api/v1`，不要直接在 `main.py` 添加业务路由。若供前端使用，额外记录字段、枚举、分页和文件响应的影响。

### 数据库变更

先判断是否需要新表、字段、索引、唯一约束、关联表、数据回填或权限 seed。schema 变化使用 Alembic；涉及旧安装、初始化 SQL 或权限目录时同步更新对应资源和测试。不要依赖应用启动时隐式执行不可重复 DDL。

### 安全或权限变更

枚举所有可以修改目标资源的写入口，包括单条、批量、导入、重置、关联、租户切换、后台任务和运维入口。权限保护不能只加在列表或一个主 endpoint 上。

### 缺陷修复

先复现具体路径并定位根因，再做最小修复。优先添加一个能在修复前失败、修复后通过的回归测试；不要用放宽断言、重新启用旧接口或吞掉异常来“修复”测试。

## 3. 实现顺序

推荐顺序：

1. DTO/DO/配置合同（如需要）。
2. DAO 查询和事务边界。
3. Service 业务规则、权限、租户和数据范围。
4. Controller 路由、依赖、`summary`、参数描述和响应模型。
5. 权限种子、迁移、README 或 `.env` 示例。
6. 精准测试，再跑完整单元测试。

Controller 应保持薄：读取参数、注入依赖、调用 Service、返回 DTO。复杂 SQL 放 DAO，跨表业务和安全判断放 Service；不要为了一个简单映射建立多余抽象。

接口联动时按以下顺序核对：后端路由和 DTO → 响应拦截器/错误处理 → 前端 API 类型和请求封装 → 页面或 composable 调用 → 两端回归验证。后端字段改名不能只依赖前端兼容映射。

## 4. 测试和验证

### 本地快速验证

Windows PowerShell 中显式覆盖环境变量，避免继承到无效的 `DEBUG=release`：

```powershell
$env:APP_ENV = "development"
$env:DEBUG = "true"
poetry run python -m pytest -q
```

### 分层验证

```bash
# 语法和导入
poetry run python -m compileall -q main.py module_admin config middleware interceptors scripts alembic test

# 单元和接口测试，不连接真实基础设施
poetry run python -m pytest -q -m "not integration"

# 覆盖率门槛由项目配置文件决定
poetry run python -m pytest -q -m "not integration" --cov --cov-report=term-missing

# 格式和静态检查
poetry run black --check path/to/changed_file.py
poetry run isort --check-only --profile black .
poetry run flake8 --max-line-length=88 .
```

集成验证前确认 Docker Desktop、MySQL、Redis 和选定环境文件可用：

```bash
docker compose --env-file .env.development up -d fastapi-mysql fastapi-redis
poetry run python -m scripts.migrate_database
RUN_INTEGRATION_TESTS=1 poetry run python -m pytest -q -m integration
```

集成测试应使用随机临时数据并清理自己创建的行，不能依赖固定业务 ID。报告测试时区分“已收集”“本地单元通过”和“真实 MySQL/Redis 已执行”。

## 5. 迁移和部署验证

修改迁移后至少检查：

```bash
poetry run alembic upgrade head --sql > migration.sql
poetry run python -m scripts.migrate_database
docker compose --env-file .env.development config
```

迁移 SQL 只用于审阅或发布前检查；真正写入数据库必须由受控迁移流程执行。变更索引、唯一约束、权限 seed 或初始化数据时，要核对重复执行、旧版本升级和失败回滚影响。

启动顺序必须是 MySQL/Redis 健康 → `fastapi-migrate` 成功 → `fastapi-app` 启动。检查 `/api/v1/health/live` 和 `/api/v1/health/ready`，ready 必须同时反映 Redis、MySQL 和 schema 状态。

生产配置还要确认真实密钥、受限 Host/CORS、Redis 密码、文档 Token、指标 Token、文件后端和 OSS/SMTP 等开关没有使用示例值。不要把 `docker compose down -v` 作为默认排障步骤；它会删除持久化数据。

## 完成定义

只有同时满足以下条件才可以报告任务完成：

- 需求行为和 API/数据库合同与当前代码一致。
- 权限、租户、数据范围、事务、幂等和敏感数据处理已按影响范围检查。
- 相关回归测试存在并通过；必要时真实 MySQL/Redis 集成测试已单独执行并明确记录。
- 迁移、权限 seed、配置示例和文档已同步，且没有真实密钥或不应提交的生成物。
- 已检查最终工作区 diff，确认没有覆盖用户修改或引入无关文件。
- 对未验证的 Docker、OSS、SMTP、OIDC/LDAP、生产部署或远程操作明确标注。

## 6. 文档和交付

实现后更新与行为直接相关的 `.codex` 文档、README、配置示例、权限 seed 或迁移说明。新代码注释和 docstring 使用中文，并解释边界或原因，不写重复代码表面含义的注释。修改接口时同步记录前端影响和未完成的联调项。

最终汇报应包含：修改文件和行为、测试命令及结果、未执行的外部依赖验证、可能的迁移或前端合同影响。不要声称未运行的 Docker、OSS、SMTP 或生产验证已经通过。

## 7. 版本控制约定

提交保持小而原子，使用现有约定前缀：`feat:`、`fix:`、`refactor:`、`docs:`、`test:`、`perf:`、`chore:`。除非用户明确要求，不自动提交、推送、创建 PR 或修改无关文件。
