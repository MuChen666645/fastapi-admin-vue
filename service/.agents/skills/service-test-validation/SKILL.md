---
name: service-test-validation
description: 为 FastAPI 管理服务选择并执行精准、完整、离线和集成验证。修改服务代码或测试，诊断 pytest/import 失败，验证路由、认证、Redis、MySQL、会话行为，或编写真实验证报告时使用。
---

# Service 测试验证

用于根据变更边界选择验证深度，并严格区分本地测试、Docker、MySQL、Redis、第三方服务、前端和生产验证。

## 工作流程

1. 先记录工作区状态并识别改动层次，不覆盖无关用户修改。
2. 导入 `main` 或新建异步测试前先读 `test/conftest.py`。本项目可能要求在导入前设置环境变量，并注入 fake Redis、Limiter、应用状态和日志配置。
3. 选择最小有效测试范围：
   - Controller、DTO、路由：最近的 API/模块测试。
   - 认证、权限、租户、数据范围、Token、Redis：安全与授权测试，再扩大到共享 API 测试。
   - 会话、中间件、响应、应用工厂、生命周期：相关横切测试和完整测试。
   - 迁移或启动 SQL：离线 Alembic SQL 以及迁移/schema/SQL-init 测试。
4. API 行为优先使用进程内异步测试：`httpx.ASGITransport(app=app)`、测试工厂、fake 依赖和明确的 app state。测试收集成功不等于测试执行成功。
5. 使用 Poetry，并在 PowerShell 中控制继承配置：

```powershell
$env:APP_ENV = "development"
$env:DEBUG = "true"
poetry run python -m pytest -q
```

6. 共享边界变更时扩大检查：

```powershell
poetry run python -m pytest -q
poetry run python -m compileall -q main.py module_admin config middleware interceptors scripts alembic test
git diff --check
```

7. 只有确认 MySQL、Redis、Docker 和环境文件可用后才运行 integration。测试使用随机隔离数据并清理自己创建的记录；服务不可用时明确标记为未执行。
8. 从第一条 traceback 定位原因。常见原因包括解释器错误、导入 `main` 前未设置环境、SlowAPI 限流、Windows 日志多进程行为、静态路由顺序、响应包装漂移和 fake Redis/验证码契约漂移。
9. 报告精确命令及结果：目标测试、完整单元/API 测试、离线迁移检查、integration、compile/style 检查以及未执行项。

## 完整性规则

- 不放宽断言、权限、类型、校验或 fixture 合同来掩盖缺陷。
- 不通过增加生产降级状态来掩盖导入失败。
- 不把本地单元测试结果描述成 MySQL、Redis、Docker、OSS、SMTP、OIDC、LDAP、浏览器、前端或生产验证。
- `compileall` 产生的缓存文件不得加入改动。

选择跨层覆盖范围时读取 [test-matrix.md](references/test-matrix.md)。
