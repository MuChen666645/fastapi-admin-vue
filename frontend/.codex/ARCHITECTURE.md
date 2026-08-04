# 前端架构

本文描述当前 `frontend/src` 的真实依赖关系和运行时流程。新增代码应沿用这些边界；如果需要改变边界，先更新设计和对应测试。

## 总体依赖

```text
页面 / 布局组件
    -> hooks 或 Pinia Store
    -> 领域 API（仅通过 @/api）
    -> utils/request.ts
    -> Alova fetch adapter
    -> FastAPI
```

路由是另一条横向基础设施：

```text
main.ts
    -> App.vue
    -> Router
        -> 静态路由 modules
        -> auth guard
        -> /user/routes
        -> route-utils 本地组件白名单
        -> router.addRoute('app', route)
```

页面组件不能绕过 Store/API/Router 的职责边界；公共出口只负责导出，不创建实例、不发请求、不触发导航副作用。

## 目录职责

| 目录或文件                            | 当前职责                                                           |
| ------------------------------------- | ------------------------------------------------------------------ |
| `src/api/<domain>/index.ts`           | 领域请求函数和请求参数编码                                         |
| `src/api/<domain>/parsers.ts`         | 对 `unknown` 响应进行运行时校验和转换                              |
| `src/utils/request.ts`                | Alova 实例、基地址、Authorization、响应解包、错误归一化、401 刷新  |
| `src/utils/request-feedback.ts`       | 注册并触发全局请求 Message 回调                                  |
| `src/utils/guards/api.ts`             | 基础值和统一响应结构守卫                                           |
| `src/utils/guards/route.ts`           | 动态路由路径、名称、菜单类型和外链的安全校验                       |
| `src/router/modules`                  | 静态路由记录：public、protected、error                             |
| `src/router/guards/auth.ts`           | 会话初始化、密码变更重定向、动态路由注册和 not-found 恢复          |
| `src/router/route-utils.ts`           | 后端路由校验后的组件解析、容器重定向和 RouteRecord 转换            |
| `src/router/route-source.ts`          | 统一从后端获取用户路由                                             |
| `src/stores/modules/auth.ts`          | Token、用户、权限、路由和会话状态                                  |
| `src/stores/modules/tabs.ts`          | 标签页列表和缓存标签名                                             |
| `src/stores/modules/route-loading.ts` | 全屏/内容区 Loading 状态和最短显示时间                             |
| `src/stores/modules/preferences.ts` | 外观、布局、通用偏好和 `localStorage` 持久化                   |
| `src/stores/modules/layout-settings.ts` | 统一偏好 Store 的旧布局兼容导出                               |
| `src/hooks`                           | Lottie、主题、语言、ECharts 和路由缓存等依赖上下文的可复用行为     |
| `src/utils/index.ts`                  | 无生命周期的公共工具包入口：图标、本地化、主题选项和 Lottie 基础函数 |
| `src/components`                      | 全局 Loading、请求 Message 桥、路由进度条、面包屑等跨页面组件       |
| `src/layouts/BasicLayout`             | 侧边栏、头部、标签页、内容区、ContentLoading、KeepAlive 和页脚     |
| `src/views`                           | 语义化路由级页面；页面私有业务组件放在对应页面的 `components/`     |
| `src/types`                           | API DTO、路由、Store、传输、页面和测试类型；所有类型声明的唯一归属 |

当前没有 `src/composables/` 目录。新增可复用页面行为优先放入 `src/hooks/`，不要为了目录形式新建第二套抽象。

## 组件、工具函数和 Hooks 分层

| 场景 | 放置位置 | 可以承担的职责 | 明确禁止 |
| ---- | -------- | -------------- | -------- |
| 跨页面公共 UI | `src/components/<name>/` | 展示、交互、Props/Emits、局部校验、局部 Loading | 领域 API、业务列表、Token、跨页面业务状态 |
| 页面专属 UI | `src/views/<domain>/<page>/components/` | 页面内展示和交互编排 | 被无关页面直接依赖，或重复实现公共基础组件 |
| Vue/Router/Pinia 上下文行为 | `src/hooks/use*.ts` | 生命周期、DOM Ref、Router 监听、Store 驱动的共享 UI 行为 | 领域请求、后端响应解析、模块级业务状态 |
| 无生命周期公共逻辑 | `src/utils/` | 纯计算、格式化、解析、转换和安全校验 | 依赖组件上下文、隐式全局状态、未经说明的业务副作用 |
| 传输和运行时守卫 | `src/utils/request.ts`、`src/utils/guards/` | 请求发送、响应包装、`unknown` 校验和动态路由安全校验 | 页面直接调用、绕过 API 领域层或放宽校验 |

推荐依赖方向为：

```text
页面 / 页面专属组件
    -> 公共组件
    -> Hooks / Pinia Store
    -> @/api

公共组件 -> Hooks / Utils
Hooks     -> Utils / Pinia / Router
API parser -> Utils guards
Utils     -/-> 页面、组件、Router 实例和领域 Store
```

组件、Hook 和工具的公开合同必须同时由源码、`src/types/` 类型、所属 README 和测试表达。组件 README 记录 Props、Emits、Slots、暴露方法、校验与状态；Hook README 记录依赖上下文、返回值和清理行为；工具 README 记录公共入口、副作用边界、失败处理和安全限制。

新增代码的选择顺序：先判断是否只是纯函数；若需要生命周期或 Router/Pinia 上下文则使用 Hook；若需要跨页面状态则使用 Store；若需要 API 或响应解析则使用领域 API；只有跨页面复用的 UI 才放入公共组件。

## API 数据流

1. 页面或 Store 从 `@/api` 调用领域函数。
2. 领域函数调用 `requestJson(path, options, parser)`。
3. `request.ts` 添加访问令牌，发送请求并验证统一响应包装。
4. 非 2xx 或业务 `code` 非 2xx 转换为 `ApiError`。
5. 401 在允许刷新时通过共享 `refreshPromise` 单飞刷新令牌并重试一次；刷新结果会校验会话版本和当前刷新令牌，避免旧会话回写。
6. parser 校验 `payload.data`，失败时转成安全的 `ApiError`。
7. Store 或页面只接收已验证的领域类型。

不要在页面处理原始响应、重复解包、重复刷新或猜测错误字段。

## 会话生命周期

```text
登录页
  -> login API
  -> applyTokens
  -> initializeSession
      -> must_change_password ? 修改密码状态 : 当前用户 + 权限 + /user/routes
  -> authenticated
  -> router guard 注册动态路由
```

- 没有访问令牌时，如果有刷新令牌则先调用 refresh API；刷新失败会清空会话。
- `must_change_password` 为真时不调用当前用户和路由接口，守卫只允许进入修改密码页。
- 初始化请求通过 `initializationPromise` 去重；失败后允许后续重新初始化。
- 退出登录始终清理 Token、用户、权限、动态路由依赖的 Store 状态和标签页。
- Pinia 持久化保存 auth Store 的刷新令牌/记住的用户名和 tabs Store 的标签页；`preferences` Store 使用 `localStorage` 保存非敏感 UI 偏好。登录偏好工具另有浏览器存储行为，见 `PROJECT.md` 的已知风险。

## 路由架构

### 静态路由

`src/router/modules/index.ts` 汇总：

- `public.ts`：`/login`。
- `protected.ts`：`/change-password` 和 `app` 布局；`app` 下包含认证后的 `/system/settings` 系统设置入口，以及“演示 / 缺省页 / 403、404、500、网络离线”静态菜单树。
- `error.ts`：`/403`、`/500`、`/offline` 和通配 not-found。

项目不再有 `VITE_ROUTE_MODE`。认证后业务菜单和页面始终来自后端 `/user/routes`。

### 动态路由

`parseUserRoutes` 负责响应边界校验：

- 路径拒绝 `..`、反斜杠、重复斜杠、查询/空白和非允许字符。
- 路由名称限制长度和字符集。
- 菜单类型只接受 `C`、`L`、`I`、`W`。
- 外链只接受无用户名密码的 `http`/`https` URL。
- 子路由逐项解析，重复路由名称只保留第一次出现的节点。

`buildDynamicRoutes` 再将组件字段标准化并映射到 `src/views/**/*.vue`：

- 支持 `home/index`、`@/views/home/index.vue`、`../views/home/index.vue`、`./views/home/index.vue` 和 `/views/home/index.vue`。
- 只从 `import.meta.glob('../views/**/*.vue')` 得到的本地 loader 中选择组件。
- 缺少组件的叶子路由会被过滤，并由 `console.warn` 输出一次警告。
- 没有组件但有可导航子节点的容器路由使用 `RouterView` 并自动重定向到第一个子节点。
- 外链菜单允许没有本地组件，但不能把外链交给任意组件导入。

注册通过 `router.addRoute('app', route)` 完成；名称已存在的动态路由不会重复注册。清理只删除本次注册的动态名称，静态路由不会被清理。

### 认证守卫

- 访问公开路由直接放行。
- 访问受保护路由先初始化会话；无会话时跳转登录并保留 redirect。
- 访问 `app` 时注册动态路由并跳到第一个可见本地页面，没有可见页面则进入 403。
- 访问 not-found 时会先注册动态路由，再重新解析原路径，支持刷新动态路由页面。
- 密码变更状态访问其他受保护路由会重定向到 `change-password`。

## 页面、标签页与 KeepAlive

`BasicLayout` 的内容结构为：

```text
NLayout
├── AppSidebar
├── main-layout
│   ├── AppHeader
│   ├── AppTabs
│   └── NLayoutContent
│       ├── ContentLoading
│       └── RouterView -> KeepAlive -> 页面组件
└── AppFooter
```

布局偏好由 `usePreferencesStore` 驱动，`useLayoutSettingsStore` 只是兼容别名：`content` 模式固定右侧布局并让内容区内部滚动，`workspace` 模式让右侧工作区整体滚动，`sticky` 模式只固定头部和标签栏并让其余右侧内容滚动。侧边栏、标签栏、面包屑、页脚和内容宽度开关也由该 Store 统一控制。

- 页面路由的 `meta.noCache === false` 才允许缓存。
- `useRouteCache` 为可缓存页面创建 `RouteTab_<route-key>` 包装组件，避免直接使用同一个页面组件名造成 KeepAlive 串缓存。
- 当前路由和标签页 Store 中的可缓存标签共同组成 KeepAlive `include`。
- 标签页列表持久化和组件缓存是两个概念：关闭标签会移除列表，刷新标签通过增加 `routeViewKey` 重建页面实例，但不等同于清空全部 tabs 持久化数据。

## Loading 与动画

```text
Router beforeEach
    -> route-loading.start(screen/content)
Router afterEach / onError
    -> setScope
    -> route-loading.finish()
    -> 最短 240ms 后隐藏
```

- `GlobalLoading` 在 App 根部监听 Router，负责布局外的全屏遮罩和初始导航。
- 进入 `app` 后，`ContentLoading` 在 `NLayoutContent` 内显示，布局内页面切换不遮挡侧边栏、头部和标签页。
- 已缓存路由的导航会跳过 Loading 启动。
- Lottie 播放器的创建、播放、暂停和销毁必须通过 `utils/lottie.ts` / `hooks/useLottie.ts`，组件卸载时销毁实例。
- `RouterLoadingBar` 独立使用 Naive UI LoadingBarProvider，不能与 Lottie Store 互相修改内部状态。

## 类型、样式和页面目录

- 所有 `type`、`interface`、`enum` 声明集中在 `src/types/` 的语义化领域文件中，业务代码通过 `@/types` 导入；即使只被一个页面使用，也不在 `views` 或组件文件内声明。
- 新增普通布局、间距、颜色、排版和响应式规则时优先写 UnoCSS utility class；`<style scoped>` 只承载 utility 不适合表达的组件专属规则。
- `src/views/<domain>/<page>/` 的每一级目录都应表达业务域或页面职责，页面文件通常使用 `index.vue`，避免无语义的目录名。后端 `component` 路径必须与该语义化目录结构一致。

## 主题与图标

- `useTheme` 使用 `localStorage` 保存 `fastapi-admin:theme`，App.vue 将暗色状态同步到 Naive UI 和根节点 class。
- `utils/icon.ts` 只从已静态导入的 Ionicons5 对象中按后端图标名查找，未知名称返回 `null`，不猜测别名或动态导入；详情见 `src/utils/README.md`。

## 偏好与本地化依赖 / Preference and locale dependency

```text
App.vue
  -> usePreferencesStore
      -> useTheme / useDocumentTitle / useLocale
      -> root CSS variables and shell behavior
  -> BasicLayout and system settings
```

`useLocale` 只负责前端界面文案；它不翻译或修改后端业务数据、权限码、菜单契约和错误字段。`useDocumentTitle` 只对已知静态路由标题使用词典，动态标题保持原文。`autoUpdate` 没有隐藏网络请求，避免在没有后端契约时制造假接口。
