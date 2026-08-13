# 仓库协作架构

## 请求数据流

```text
Vue 页面 / Store
  -> frontend API 类型与 Parser
  -> frontend request.ts
  -> HTTP /api/v1
  -> FastAPI Controller
  -> Auth / Tenant / Data Scope
  -> Service 业务规则与事务
  -> DAO / SQLModel
  -> MySQL / Redis / Worker / 外部服务
  -> 响应拦截与前端错误归一化
```

页面和布局不直接访问传输层；Controller 不承载业务规则；DAO 不承载 HTTP 或授权语义。

## 身份、租户和权限

登录建立会话，后端验证 Token、用户状态、权限、租户和数据范围；前端 Store 保存会话体验并初始化服务端路由。
租户切换、管理员保护、资源所有权和跨租户拒绝必须在后端完成，前端只同步可见性、禁用态和错误反馈。

## 路由与布局

前端保留公开/认证静态路由，业务菜单由后端提供并经本地组件白名单转换。BasicLayout 管理标签、缓存、
系统设置抽屉和内容区 Loading；这些 UI 状态不得改变 API、权限或租户状态。

## 数据库和后台任务

schema 由 Alembic 版本链和初始化/升级 SQL 管理；新增变更保持幂等、可审阅并同步模型、DAO、Service、权限 seed 和测试。
调度器、Worker、导出、通知和清理任务使用独立会话及明确超时、重试、锁、取消和关闭行为，不能阻塞 HTTP 请求。

## 验证层次

```text
静态检查 -> 单端目标测试 -> 跨端契约测试 -> 构建/离线迁移 SQL
         -> Docker/MySQL/Redis/浏览器/第三方联调 -> 目标环境发布验证
```

每一层都必须单独记录结果，前一层通过不代表后一层已验证。
