# 后端架构

## 请求流

```text
FastAPI 路由
  -> 认证、授权、租户上下文、DTO 绑定
  -> Service 业务规则与事务边界
  -> DAO 查询或持久化
  -> SQLModel / MySQL
  -> 统一响应与异常拦截
```

Controller 保持轻薄；Service 承担领域规则、事务与预期异常决策；DAO 只读写数据，
不得承载业务策略或返回 HTTP 响应。

## 运行时横切能力

- `ResponseInterceptor` 规范普通 API 响应。
- `ApiExceptionInterception` 处理应用异常，不暴露堆栈。
- 幂等、限流、日志、可观测性、受信 Host 校验和遥测均由 `main.py` 配置。
- Redis 提供会话、验证码、限流、幂等、调度等短期协调能力；MySQL 是持久化事实来源。

## 身份、授权与租户

认证、RBAC、租户上下文、数据范围、用户状态和敏感操作均由服务端控制。Controller
声明依赖，Service 校验业务归属与受保护账户规则，DAO 通过既有辅助方法应用租户与数据
范围条件。客户端租户标识或隐藏的 UI 控件本身不授予任何访问权限。

## 后台任务

长任务由调度器、队列 Worker 或生命周期 Worker 执行。请求处理器不得在请求路径执行
无界任务。任务处理器显式注册，执行状态应持久化且可观测。
