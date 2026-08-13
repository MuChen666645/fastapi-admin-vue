# 项目开发文档

## 1. 项目概览

本仓库由两个通过 HTTP 契约协作的应用组成：

| 项目        | 技术栈                                                  | 责任                                             |
| ----------- | ------------------------------------------------------- | ------------------------------------------------ |
| `frontend/` | Vue 3、TypeScript、Vite、Pinia、Alova、Naive UI、UnoCSS | 管理端页面、交互、会话体验和类型化 API 调用      |
| `service/`  | FastAPI、SQLModel、MySQL、Redis、Alembic、Poetry        | 认证、授权、租户、业务规则、数据一致性和后台任务 |

后端是认证、授权、租户、数据范围、业务状态和数据一致性的最终权威。前端菜单、按钮和
路由守卫只改善体验，不能替代服务端校验。

## 2. 开始开发

修改前依次阅读：

1. 根目录 `AGENTS.md`、`.codex/README.md` 和适用的根级 Skill。
2. 目标项目的 `AGENTS.md`、`.codex/README.md` 和适用领域 Skill。
3. 受影响源码、DTO、类型、配置、迁移、调用方和测试。

常用本地命令：

```powershell
# 前端
Set-Location frontend
pnpm install
pnpm run check
pnpm run test:run
pnpm run build

# 后端
Set-Location ..\service
$env:APP_ENV = "development"
$env:DEBUG = "true"
poetry install
poetry run python -m pytest -q
poetry run python -m compileall -q main.py module_admin config middleware interceptors scripts alembic test
poetry run alembic upgrade head --sql
```

前端运行要求以 `frontend/package.json` 的 `engines` 为准；后端真实 MySQL、Redis、Docker、
第三方服务和浏览器验证必须单独确认，不以本地单元测试替代。

## 3. 端到端开发规范

涉及接口或业务联动时，先建立契约记录：

- 请求方法、完整 `/api/v1` 路径、Query、Path、Body、FormData 和分页参数。
- 成功响应、分页结构、空值、错误结构、文件/流响应和响应包装规则。
- 登录态、刷新 Token、权限码、租户、数据范围和资源所有权要求。
- 状态枚举、时间格式、排序语义、幂等、重试、并发和失败回滚行为。

实现顺序为：后端 DTO/Controller/Service/DAO 或既有契约核验，前端 API 类型/Parser/Store/页面
同步变更，最后补充两端回归测试。不得新增假接口、猜字段、静默 Mock 或以客户端权限替代后端授权。

## 4. 交付质量门禁

- 代码、类型、Lint、格式和目标测试通过。
- 接口、权限、租户、错误、Loading、重复提交和异常清理路径已覆盖。
- 数据库变更具备 Alembic/初始化 SQL 依据、离线 SQL 检查和真实数据库执行说明。
- 无 Token、密码、密钥、验证码、生产数据、覆盖率产物、缓存或临时构建物进入改动。
- 最终执行 `git diff --check`，并如实报告未验证项和剩余风险。

## 5. 变更边界

前端任务默认只修改 `frontend/`，后端任务默认只修改 `service/`。跨项目修改必须由接口契约
或用户需求明确要求，并在交付中列出前后端文件、接口字段、错误语义、权限和测试影响。

提交保持小而原子，使用 `feat:`、`fix:`、`refactor:`、`docs:`、`test:`、`perf:` 或 `chore:` 前缀。
未经明确要求，不提交、推送、创建 PR 或操作远程/生产资源。
