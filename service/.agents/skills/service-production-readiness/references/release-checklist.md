# 发布检查表

## 配置和安全

- [ ] 生产/staging 已关闭 Debug，Hosts、CORS 和 headers 使用受限值。
- [ ] Secret、数据库密码、Redis 密码、docs token 和 metrics token 来自安全配置，不在仓库中出现真实值。
- [ ] 上传大小、扩展名、内容探测、临时文件和清理策略已检查。
- [ ] 日志、错误和指标不泄露 Token、密码、密钥或完整敏感请求体。

## 启动和依赖

- [ ] MySQL/Redis healthcheck 配置存在且实际可用。
- [ ] `fastapi-migrate` 在应用和 Worker 前成功完成。
- [ ] Web 使用容器服务名，宿主机运行使用正确的 `127.0.0.1` 配置。
- [ ] Web 生命周期没有隐式执行不可控 schema DDL。

## 健康和运行时

- [ ] liveness 不依赖外部服务或请求级会话。
- [ ] readiness 检查 Redis、MySQL 和 schema 状态。
- [ ] 后台任务、Scheduler、Worker、Redis 和 MySQL 有明确关闭和异常处理。
- [ ] 资源限制、重试、超时、锁 TTL 和告警配置已核对。

## 验证结果

- [ ] Compose 配置检查实际通过。
- [ ] 本地测试实际通过。
- [ ] Docker、MySQL、Redis、第三方和生产环境验证分别记录。
- [ ] 未执行项和剩余风险明确列出。
