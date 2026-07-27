# 测试矩阵

| 变更范围 | 首选验证 | 需要扩大时 |
| --- | --- | --- |
| 单个 DTO/Controller | 对应模块测试 | 完整 API 测试 |
| 认证、RBAC、租户、数据范围 | 安全和授权测试 | 完整测试、Redis integration |
| Redis Token、验证码、限流、幂等 | 对应安全/限流测试 | 完整测试、真实 Redis |
| 请求会话、DAO、事务 | 会话和 DAO 测试 | 完整测试、真实 MySQL |
| ResponseInterceptor/Observability | 中间件测试 | 完整 API 测试 |
| main/lifespan/health | app factory、health 测试 | Docker Compose、真实依赖 |
| Alembic/初始化 SQL | 离线 SQL、migration/schema/sql-init 测试 | fastapi-migrate、真实 MySQL |
| Worker/调度/通知/导出 | Service 单元测试 | Redis/MySQL/Worker integration |

## 结果分类

- `通过`：命令实际执行且退出成功。
- `未执行`：因 Docker、数据库、Redis、第三方服务或权限不可用而没有运行。
- `未覆盖`：当前验证没有触及该行为，不得写成通过。
- `失败`：命令执行但有失败，报告第一条可复现错误和影响范围。
