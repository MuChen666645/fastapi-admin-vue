---
name: frontend-auth-rbac
description: 追踪、实现或加固 Vue 管理端登录、令牌刷新、会话初始化、密码变更跳转、权限指令、路由守卫、租户相关 UI 和浏览器存储边界。修改 frontend/src/api/auth、stores/modules/auth、router/guards、权限 Hook/指令或安全回归测试时使用。
---

# Frontend 认证与权限体验

用于维护前端会话和权限体验；服务端仍负责所有认证、授权、租户和数据范围的强制校验。

## 工作流程

1. 读取相关认证 API、`useAuthStore`、`request.ts`、路由守卫、权限工具/指令、静态路由和
   对应后端认证与授权契约。
2. 枚举路径：登录、刷新、初始化用户/权限/路由、登出、会话失效、强制改密、重定向、租户
   切换，以及受权限控制的页面和操作。
3. 复用 `useAuthStore`、统一请求层和现有守卫；不得新增第二套 Token、刷新、权限或浏览器
   存储机制。
4. 使用 `hasPermission`、权限 Hook 与指令统一计算可见性；权限列表和 `*:*:*` 的语义必须与
   现有实现一致。任何受保护 handler 仍须具备页面内防护和 Loading/重复提交控制。
5. 对服务端动态路由只信任经 `route-utils.ts` 白名单解析的本地视图；无效路径必须拒绝，不得
   传入任意 `import()`。
6. 明确区分未登录、会话失效、无前端可见权限、后端拒绝、资源不存在与租户不匹配，避免用
   空数据掩盖拒绝结果。
7. 增加针对登录/刷新、守卫重定向、权限变化、超级权限和无权限操作的回归测试。

## 禁止事项

- 不在 URL、日志、测试夹具、截图或非必要持久化中泄露 Access Token、Refresh Token、密码、
  验证码、MFA 或重置令牌。
- 不将前端菜单、按钮或守卫描述为后端授权替代品。
- 不硬编码 `admin`、用户 ID、租户 ID 或权限码绕过真实会话状态。
- 不通过放宽类型、权限检查或断言使安全测试通过。

详细检查项见 [authorization-ui-checklist.md](references/authorization-ui-checklist.md)。
