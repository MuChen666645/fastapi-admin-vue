# 前端架构规则

## 总体数据流

业务代码遵循单向依赖：

```text
页面或组件
    -> composable 或 Pinia Store
    -> 领域 API 模块
    -> 统一传输层
    -> FastAPI
```

禁止页面直接拼接 URL、调用 Alova、管理全局 Token、解析复杂后端响应或根据服务端字符串动态导入组件。

## 目录和模块职责

| 目录 | 模块职责 | 统一出口 | 禁止承担的职责 |
| --- | --- | --- | --- |
| `src/api/<domain>` | 领域接口、请求 DTO 适配、响应解析和接口函数 | `src/api/<domain>/index.ts`、`src/api/index.ts` | 页面展示、路由跳转、权限猜测、Store 状态 |
| `src/components` | 可复用展示和交互组件 | 按组件目录提供 `index.vue`，需要时由组件目录 `index.ts` 汇总 | 复杂业务请求、全局会话和领域权限策略 |
| `src/composables` | 可复用页面行为、生命周期、取消和局部状态 | `src/composables/index.ts`（存在多个领域时） | 直接定义跨模块权限策略和重复请求协议 |
| `src/router/modules` | 分领域静态路由定义 | `src/router/modules/index.ts`、`src/router/index.ts` | 业务请求和后端授权决策 |
| `src/router/guards` | 认证、动态路由和安全重定向守卫 | `src/router/guards/index.ts` | 声明业务页面和修改 Store 之外的全局数据 |
| `src/stores/modules` | 按领域管理 Pinia 状态和动作 | `src/stores/modules/index.ts`、`src/stores/index.ts` | DOM、页面组件、直接请求和服务端密钥存储 |
| `src/types` | 共享类型、领域 DTO 和路由类型 | 领域 `index.ts`、`src/types/index.ts` | 网络请求、路由跳转和隐式副作用 |
| `src/utils` | 纯函数、传输边界和运行时守卫 | 按领域或用途提供统一出口 | 隐式导航、隐式请求和全局业务状态 |
| `src/views` | 路由级页面和页面编排 | 由路由模块引用，不作为业务公共出口 | 重复实现 API、类型、权限和通用交互 |

## 类型架构

类型必须按领域拆分，目标结构如下：

```text
src/types/
├── api/
│   ├── common.ts       # ApiResponse、分页和通用错误
│   ├── auth.ts         # 登录、刷新、验证码和密码找回 DTO
│   ├── user.ts         # 当前用户和用户权限 DTO
│   └── index.ts
├── router.ts           # 服务端路由 DTO、RouteMeta 和路由类型
├── store.ts            # 跨 Store 的状态类型
└── index.ts
```

- 类型文件只声明类型和值对象，不导入 API、Store、Router 或 Vue 组件。
- UI 表单类型可以放在对应领域类型文件中，例如 `types/auth.ts`，不能在页面中定义可复用类型。
- 后端蛇形字段在 API 类型中原样保留；页面需要驼峰字段时由明确命名的适配函数转换。
- 运行时响应校验放在 `src/api/<domain>/parsers.ts` 或 `src/utils/guards/<domain>.ts`，解析器接收 `unknown`，校验后才返回领域类型。
- 旧的 `src/types/api.ts` 只能作为迁移兼容入口，新的类型不得继续添加到该聚合文件；迁移完成后由 `src/types/api/index.ts` 统一导出。

## API 架构

```text
src/api/
├── auth/
│   ├── index.ts        # 对外接口函数和领域导出
│   └── parsers.ts      # auth 响应运行时校验
├── user/
│   ├── index.ts
│   └── parsers.ts
└── index.ts             # 前端 API 唯一公共出口
```

- `src/utils/request.ts` 集中处理 API 基地址、版本前缀、Authorization、统一响应解包、HTTP/code 错误、超时和 401 单飞刷新。
- 领域 API 文件只声明方法、路径、请求编码、参数和解析器；不得重复实现鉴权、响应解包和错误归一化。
- `src/api/index.ts` 只做显式领域导出，例如 `export { login } from './auth'`；导出命名冲突必须显式解决。
- 页面和 Store 从 `@/api` 导入公共 API；只有 API 根出口内部可以引用领域实现文件。
- API 响应遵循：

```ts
type ApiResponse<T> = {
  code: number
  error_code?: string | null
  message: string
  data: T | null
}
```

## 路由架构

```text
src/router/
├── modules/
│   ├── public.ts        # 登录、找回密码、错误页等公开路由
│   ├── system.ts        # 系统业务静态路由
│   └── index.ts         # 路由模块统一出口
├── guards/
│   ├── auth.ts          # 登录态、must_change_password 和安全重定向
│   ├── dynamic.ts       # 服务端路由校验和本地组件白名单
│   └── index.ts
├── dynamic.ts           # 动态路由转换的兼容或实现模块
└── index.ts             # createRouter、模块注册和对外路由出口
```

- `router/index.ts` 只负责创建 Router、注册模块、安装守卫和暴露清理/注册函数，不堆放所有业务路由。
- 每个路由模块只导出 `RouteRecordRaw[]` 或明确的路由工厂，不调用 API、不直接修改 Token。
- 守卫必须保留公开路由、登录态、`must_change_password`、动态路由校验和安全重定向的既有语义。
- 服务端返回的 `path`、`name`、`component`、`redirect`、`meta` 和 `children` 先经运行时守卫，再匹配静态本地组件白名单。
- 路由统一出口不得导出服务端组件路径、任意动态导入函数或隐式副作用。

## Store 架构

```text
src/stores/
├── modules/
│   ├── auth.ts          # Token、会话、用户、权限和初始化
│   ├── app.ts           # 应用级 UI 状态
│   └── index.ts
└── index.ts              # Store 统一出口
```

- 一个 Store 只负责一个领域，状态、getter、action 和持久化策略必须在领域模块内闭合。
- `auth` Store 负责访问/刷新 Token 生命周期、当前用户、权限、会话清理和初始化状态；页面不得直接修改这些状态。
- Store 可以调用 `@/api`，但不能调用具体页面、操作 DOM、执行任意导航或把 API 解析逻辑复制到 action 中。
- `src/stores/index.ts` 只显式导出 `useAuthStore` 等 Store 工厂，不在出口文件创建 Pinia 实例或注册插件。
- Store 的公共状态和参数类型放入 `src/types/store.ts` 或对应领域类型文件，不在 Store 文件尾部定义可复用类型。

## 图标架构

- 所有功能图标来自 `@vicons/ionicons5`；`@vicons/utils` 只用于统一包装、尺寸和颜色，不提供第二套图标源。
- 图标组件应在组件或领域 UI 模块中静态导入，禁止根据后端字符串拼接模块路径。
- 通用图标按钮统一通过可复用组件或明确的局部模板处理尺寸、`aria-label`、`title` 和禁用态。
- 禁止 Emoji、Unicode 字符、手写 SVG 和不同图标库混用来表达同一类操作。
