# 前端架构

## 数据流

```text
路由页面或布局
  -> Pinia 状态或页面编排
  -> src/api/<domain>/index.ts
  -> Parser 校验 unknown 数据
  -> src/utils/request.ts
  -> FastAPI API
```

`request.ts` 是唯一传输边界：附加认证、归一化 API 响应包、协调 Token 刷新，并将
失败转换为 `ApiError`。API Parser 负责响应结构校验，调用方只接收类型化领域数据。

## 会话与路由

```text
登录或刷新
  -> auth Store 写入令牌
  -> initializeSession()
  -> 当前用户、权限和服务端路由
  -> 校验后动态注册到 app
```

路由守卫负责受保护路由初始化、强制改密跳转和安全重定向。后端提供路由与授权数据，
前端拒绝格式异常记录和未知视图路径。

## 状态归属

- `auth`：令牌、用户、权限、路由和会话状态。
- `preferences`：非敏感外观、语言和布局偏好。
- `dictionary`：当前会话字典缓存。
- `tabs`：会话持久化的标签列表。
- `route-loading`：导航范围和最短可见时间。
- `message`：当前会话消息状态。

仅持久化 Store 显式配置的字段；退出登录或数据源变化时失效租户敏感和会话敏感状态。

## 布局与 Loading

`GlobalLoading` 用于初始导航和 `app` 外导航，`ContentLoading` 由 `BasicLayout`
在 `NLayoutContent` 内挂载，确保 `app` 内切换不遮挡全局导航且不随路由内容增长。
路由缓存、标签、Loading 和滚动模式必须彼此独立，均不得影响授权、API 选择或数据范围。
