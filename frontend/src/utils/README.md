# 工具包使用文档

`src/utils/` 存放无组件 UI、无页面生命周期的通用函数。纯工具优先通过 `@/utils` 入口导入；请求传输、响应守卫和全局 Message 桥接属于基础设施，继续从对应的具体模块导入，避免把副作用模块误当作普通工具。

## 公共入口

```ts
import { findAccentColor, resolveIconComponent, translateMenuTitle } from '@/utils'
```

## 工具索引

| 工具                                                                                           | 公共入口                   | 用途                                         |
| ---------------------------------------------------------------------------------------------- | -------------------------- | -------------------------------------------- |
| `resolveIconComponent`                                                                         | `@/utils`                  | 从静态 Ionicons5 集合解析菜单图标。          |
| `translateMenuTitle` / `translateRouteTitle`                                                   | `@/utils`                  | 翻译已知前端菜单和路由标题。                 |
| `findAccentColor`、`accentColorOptions`、`radiusOptions`                                       | `@/utils`                  | 读取主题色和圆角选项。                       |
| `loadLottieAnimation`、`playLottieAnimation`、`pauseLottieAnimation`、`destroyLottieAnimation` | `@/utils`                  | 管理 Lottie 实例的基础动作。                 |
| `isSafeRoutePath`、`isSafeRouteName`、`isUserRouteMenuType`、`isSafeExternalLink`              | `@/utils`                  | 校验后端路由路径、名称、菜单类型和外链。     |
| `loginPreferences`                                                                             | `@/utils/loginPreferences` | 记住登录偏好；存在敏感数据持久化风险。       |
| `request`                                                                                      | `@/utils/request`          | Alova 传输、令牌刷新、响应解析和错误归一化。 |
| `guards/api`                                                                                   | `@/utils/guards/api`       | API 响应和值的运行时校验。                   |
| `guards/route`                                                                                 | `@/utils/guards/route`     | 后端路由安全校验，亦通过 `@/utils` 导出。    |

## 图标解析

```ts
import { resolveIconComponent } from '@/utils'

const icon = resolveIconComponent('HomeOutline')
```

图标名称只能从已静态导入的 `@vicons/ionicons5` 中解析，未找到时返回 `null`。禁止将后端字符串直接传给 `import()`，也不要在工具包中增加动态组件白名单之外的加载逻辑。

原 `hooks/useIcon.ts` 只包含这个纯函数，已迁移到 `utils/icon.ts`。它不是 Vue Hook，新的代码应从 `@/utils` 导入。

## 路由安全校验

```ts
import { isSafeExternalLink, isSafeRoutePath } from '@/utils'

const validPath = isSafeRoutePath('system/users')
const validLink = isSafeExternalLink('https://example.com/docs')
```

这些方法只校验路由输入的格式和协议安全性，不能替代后端的认证、授权和业务校验。

## 本地化和主题选项

```ts
import { findAccentColor, translateRouteTitle } from '@/utils'

const accent = findAccentColor('blue')
const title = translateRouteTitle('home.title', 'zh-CN')
```

本地化工具只处理前端已知词典；未知动态菜单标题保留原文。主题选项只提供配置数据和查找函数，不直接修改 DOM 或偏好 Store。

## Lottie 基础函数

组件优先使用 `useLottie`，只有需要手动控制生命周期的基础设施才直接使用以下函数：

```ts
import { loadLottieAnimation, pauseLottieAnimation } from '@/utils'

const animation = loadLottieAnimation(container, animationData, { loop: true })
pauseLottieAnimation(animation)
```

创建实例后必须在对应组件卸载时调用 `destroyLottieAnimation`。完整生命周期封装见 [hooks/useLottie](../hooks/README.md#uselottie)。

## 基础设施模块

- `request.ts` 是唯一请求传输边界。页面和 Store 应从 `@/api` 调用领域 API，不直接调用它。
- `guards/api.ts` 只用于从 `unknown` 校验 API 响应，不能用类型断言绕过校验。
- `guards/route.ts` 集中维护动态路由输入的安全校验，API 解析器只负责调用它并组装领域数据。
- `request-feedback.ts` 由 `RequestMessageBridge` 注册全局 Message 回调，业务代码不应自行覆盖处理器。
- `loginPreferences.ts` 当前会在用户主动选择记住登录时保存账号和密码，这是已知安全风险；新代码不得扩大或复用该行为。

## 目录约束

- 纯函数和无生命周期的转换、格式化、解析、存储逻辑放在 `utils`。
- 依赖 Vue 生命周期、Router、Pinia 或组件上下文的行为放在 `hooks`。
- 领域请求放在 `api`，跨页面状态放在 Pinia Store。
- 新增公共工具优先补充 `index.ts` 和本 README；基础设施工具保留具体模块入口并补充测试。

## 新增或修改工具检查清单

1. 先确认函数不需要 Vue 生命周期、Router、Pinia 或组件上下文；需要这些依赖时改用 Hook、Store 或对应基础设施层。
2. 明确输入、输出、空值、错误和副作用；处理 `unknown`、接口响应、路由、外链或存储内容时必须先校验。
3. 适合跨模块复用的函数从 `src/utils/index.ts` 和 `@/utils` 导出；请求传输、响应守卫、存储和反馈桥等基础设施保留具体入口。
4. 不创建模块级业务状态，不修改页面、Router 或业务 Store，不用 `any`、无检查断言或默认成功值掩盖错误。
5. 同步更新本 README、必要的 `src/types/` 类型和边界测试；涉及浏览器能力时覆盖 SSR、不可用环境和清理行为。
