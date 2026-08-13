# 跨项目交付流程

## 1. 定义范围

识别功能、缺陷、重构、接口、迁移、文档或评审任务，记录目标端、影响端、用户路径和不在范围内的内容。

## 2. 建立证据

读取根规则、目标项目规则、适用 Skill、当前源码、DTO、配置、迁移、真实调用方和测试。先执行 `git status --short`，
保留无关工作区改动。

## 3. 建立契约表

对联动任务记录：

| 项目 | 内容 |
| --- | --- |
| 请求 | 方法、完整路径、Query、Path、Body、FormData、分页/排序 |
| 响应 | 成功字段、分页、空值、错误、文件/流、包装 |
| 安全 | 登录态、刷新、权限码、租户、数据范围、所有权 |
| 可靠性 | 事务、幂等、重复提交、并发、重试、回滚、缓存 |

## 4. 最小实现

后端按 `Controller -> Service -> DAO -> Database` 实现；前端按 `页面/Store -> API/Parser -> request` 实现。
复用已有类型、请求层、权限、组件、迁移和测试，不新建平行方案。

## 5. 覆盖失败路径

至少检查空数据、无权限、跨租户、非法输入、资源不存在、重复提交、超时、异常清理、Loading、禁用态和错误反馈。

## 6. 分层验证

```powershell
# 前端
Set-Location frontend
pnpm run check
pnpm run test:run
pnpm run build  # 影响构建、公共资源或发布时

# 后端
Set-Location ..\service
$env:APP_ENV = "development"
$env:DEBUG = "true"
poetry run python -m pytest -q
poetry run python -m compileall -q main.py module_admin config middleware interceptors scripts alembic test
poetry run alembic upgrade head --sql  # 影响迁移时
```

## 7. 复查与交付

执行 `git diff --check`，复查契约漂移、权限、租户、敏感数据、事务、N+1、生成物和文档。交付时列出修改文件、
验证命令与结果、未执行项和剩余风险；不声称未完成的浏览器、Docker、MySQL、Redis 或第三方联调已完成。
