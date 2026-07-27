---
name: service-production-readiness
description: 评审或改进 FastAPI 管理服务的生产就绪性，包括 Docker Compose 启动顺序、健康语义、配置、密钥、迁移、Worker、可观测性、资源限制和外部依赖边界。进行发布评审、部署变更、readiness 故障或 service/deploy/config 风险审计时使用。
---

# Service 生产就绪性

用于发布和运行时检查。必须分别说明源码证据、本地测试、Compose 配置、实时依赖检查和生产验证，不能把未执行的环境检查写成完成。

## 工作流程

1. 执行容器、迁移、真实数据读取或第三方调用前，确认目标环境、授权和数据影响。文档和测试只使用占位凭据。
2. 一起检查 `config/env.py`、`.env.*.example`、`Dockerfile`、`docker-compose.yml`、`deploy/`、`main.py`、health Controller、迁移脚本和 Worker 入口。
3. 验证启动依赖顺序：
   - MySQL 和 Redis healthcheck 先通过。
   - `fastapi-migrate` 成功后，`fastapi-app` 和 `fastapi-worker` 才启动。
   - Web/Worker 使用正确环境文件和容器 DNS。
   - 迁移不在 Web 生命周期中执行。
4. 验证健康语义：`/api/v1/health/live` 只反映进程存活，不依赖业务数据库；`/api/v1/health/ready` 按当前代码直接检查 Redis `PING`、MySQL `SELECT 1` 和 schema 状态。
5. 检查配置安全：生产/staging 关闭 Debug、限制 Hosts/CORS、使用真实生成密钥、配置 Redis 认证、保护 docs/metrics，并设置超时、重试、任务锁、上传限制和资源限制。
6. 检查生命周期：后台 Task、Scheduler、Worker、Engine、Redis、临时分片、通知、导出和保留期清理都有取消、超时、重试和关闭行为。
7. 检查安全和数据边界：日志无原始 Token/密钥，文件和导出有租户/所有者校验，运维接口需认证，容器使用最小权限，禁止用破坏性数据库操作恢复服务。
8. 检查可观测性和响应：Request/Trace ID、指标保护、错误语义、readiness 失败行为以及文件/流响应处理正确。
9. 按递增范围验证：

```powershell
docker compose --env-file .env.development.example config --quiet
poetry run python -m pytest -q
```

只有确认目标和数据影响后才执行 `docker compose up`、迁移、健康探测或第三方检查，并逐项报告结果。

## 发布门禁

- 单元测试通过不代表 Docker 启动、MySQL/Redis、Worker、第三方连通性或生产配置安全已验证。
- 不使用 `docker compose down -v`，不删除数据库或 Redis 卷作为默认修复。
- 非 Debug 环境不能无保护暴露 `/docs`、`/redoc`、`/openapi.json` 或 `/metrics`。
- 未验证 schema 迁移、依赖健康或密钥配置时，不得声称服务 ready。

详细发布检查见 [release-checklist.md](references/release-checklist.md)。
