# 后端功能开发提示词

你正在当前仓库根目录中实现一个新功能。

## 需求

- 功能名称：`<填写功能名称>`
- 业务目标：`<填写用户和业务价值>`
- 允许修改范围：`<填写目录、模块或文件>`
- 不在范围内的内容：`<填写明确排除项>`
- 是否需要数据库变更：`是/否；如是，说明表、字段、索引和迁移要求`
- 是否需要新权限：`是/否；如是，填写权限码和菜单/seed 要求`

## 项目约束

- 先读取仓库根目录 `AGENTS.md`、`service/AGENTS.md`，再读取 `.codex/PROJECT.md`、`.codex/ARCHITECTURE.md`、`.codex/WORKFLOW.md` 和 `.codex/BOUNDARY.md`。
- 先检查 `git status --short --branch`，保留用户已有修改。
- 当前管理 API 只使用 `/api/v1`，Controller 不得重复写全局前缀，也不得添加旧无前缀兼容路由。
- 遵守 `Controller -> Service -> DAO -> Database`，复用现有认证、租户、数据范围、响应包装、分页和配置机制。
- 新字段/参数使用现有 Pydantic/SQLModel 风格；API 元数据使用中文 `title`、`description` 和 `summary`。
- 所有密钥和外部服务参数使用占位符，不写入真实值。
- 不执行未授权的提交、推送、生产操作、远程写入或破坏性清理；需要时先确认目标和影响。
- 如果功能供前端使用，先核对 `frontend/.codex/PROJECT.md` 和 `frontend/src` 中实际存在的类型、调用方和页面；当前前端为基础模板，明确前端是否在本次范围内，不能凭空设计前端字段或交互。

## 执行要求

1. 搜索现有相似模块、DTO、DAO、权限依赖、迁移和测试。
2. 明确请求/响应、状态码、错误结构、权限、租户、数据范围、事务和幂等行为。
3. 给出简短实现计划，并按 DTO/DO → DAO → Service → Controller → migration/seed → tests 的顺序实现。
4. 数据库变更必须新增 Alembic 迁移；需要的初始化数据和权限码必须幂等。
5. 对所有会修改目标资源的单条、批量、导入、关联和后台任务入口做权限检查。
6. 新增单元/API 测试；跨 MySQL/Redis 的行为增加 integration 测试，并使用随机临时数据和清理逻辑。
7. 更新与功能直接相关的 README、环境示例或 `.codex` 文档。
8. 若改变接口、权限、状态、分页、时间或文件响应，列出前端影响；明确联动任务未完成时，不得宣称功能已端到端完成。

## 验证要求

至少执行与结果记录：

```powershell
$env:APP_ENV = "development"
$env:DEBUG = "true"
poetry run python -m pytest -q
```

按变更范围补充：

```bash
poetry run python -m compileall -q main.py module_admin config middleware interceptors scripts alembic test
poetry run black --check path/to/changed_file.py
poetry run isort --check-only --profile black path/to/changed_file.py
poetry run flake8 --max-line-length=88 path/to/changed_file.py
poetry run alembic upgrade head --sql > migration.sql
```

如果没有运行真实 Docker、MySQL、Redis、OSS、SMTP 或第三方身份服务，必须明确说明未验证，不能将本地单元测试结果扩展为生产验证结论。

## 交付格式

- 实现结果：`<简述行为>`
- 修改文件：`<列出关键文件>`
- API/数据库/权限影响：`<说明合同变化>`
- 测试结果：`<命令和结果>`
- 未验证项和后续风险：`<说明>`

完成前自检：行为、权限、租户/数据范围、事务、幂等、迁移/seed、测试、文档、前端影响和最终 diff 均已核对；未验证的外部系统必须明确列出。
