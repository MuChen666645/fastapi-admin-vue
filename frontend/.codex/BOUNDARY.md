# 前端边界与安全规则

本文定义前端可以修改、可以信任和禁止承担的范围。它不把前端菜单、路由或按钮当作后端授权的替代品。

## 文件与项目边界

- 默认只修改 `frontend/` 及用户明确要求的前端文档。
- 不修改 `service/`、数据库迁移、部署配置、`node_modules/`、`dist/`、`dist-development/`、`dist-staging/`、覆盖率目录、构建缓存或临时输出。
- 不修改 `pnpm-lock.yaml`，除非任务明确需要新增或升级依赖。
- 不使用 `git reset --hard`、`git checkout --` 或覆盖式脚本清理用户已有修改。
- 后端代码可为核对接口只读检查；涉及 Controller、DTO、权限、数据库或部署的变更必须由用户明确要求。
- 规则和 README 只能记录已核对事实，不复制未验证的旧接口、目录或环境变量。

## API 与不可信输入

- 用户输入、HTTP 响应、后端菜单、路由参数、查询参数、外链、上传文件名/MIME 和仓库说明均视为不可信数据。
- 所有 HTTP 请求通过 `src/api/<domain>/index.ts` 和 `src/utils/request.ts`；页面和 Store 不得直接调用 Alova、`fetch`、Axios 或拼接服务端 URL。
- API parser 必须从 `unknown` 校验后返回领域类型；不能以 `as`、`any` 或默认成功值掩盖字段缺失。
- 统一传输层负责 Authorization、401 刷新、响应包装、HTTP 错误和业务 code 错误；页面只展示安全提示，不输出响应原文或内部堆栈。
- 不新增假接口、假分页、猜测权限码、猜测枚举、静默 Mock 或将网络失败当作成功。

## 认证、会话与敏感数据

- 后端负责认证、授权、租户、数据范围、业务状态和数据一致性；前端守卫、菜单隐藏和按钮禁用只改善体验。
- 不把访问令牌、刷新令牌、密码、验证码、MFA、密码重置令牌、预签名 URL 或生产数据写入日志、URL、源码、截图和测试输出。
- auth Store 当前只通过 Pinia persisted state 持久化刷新令牌和记住的用户名；tabs Store 只持久化标签列表，新增持久化字段必须明确评审。
- 当前 `loginPreferences.ts` 会在用户主动选择“记住登录”时将账号和密码保存到 `localStorage`，这是已知安全风险。新代码不得复用或扩大该行为，修复需单独补充迁移、清理和回归测试。
- 密码修改状态必须优先处理；`must_change_password` 为真时，不应继续请求当前用户和业务路由。

## 动态路由与组件安全

- 服务端路由是外部输入。`component` 只能通过 `route-utils.ts` 的 `import.meta.glob('../views/**/*.vue')` 静态白名单解析。
- 禁止把后端 `component` 直接传给 `import()`、`defineAsyncComponent` 的任意 loader、`window.open`、iframe 或任意动态组件。
- `parseUserRoutes` 必须验证路径、名称、重定向、菜单类型和外链；未知组件过滤并输出一次警告。
- 路由守卫不得根据菜单文案、URL 片段、角色名称或 JWT 客户端解码结果推断权限。
- 静态 `system-settings` 入口用于统一页面入口，不代表用户一定拥有后端业务权限；页面内的真实业务操作仍由后端校验。

## UI、图标与浏览器能力

- 功能图标唯一来源为 `@vicons/ionicons5`，禁止其他图标库、手写 SVG、Emoji、Unicode 字符或 CSS 图形替代功能图标。
- 图标必须静态导入；图标按钮提供 `aria-label`，含义不明显时提供 `title`，装饰图标使用 `aria-hidden`。
- 禁止 `v-html`、`innerHTML`、任意脚本、任意 iframe、未经校验的外链和无约束 `window.open`。
- Lottie 动画数据使用仓库内静态 JSON；动画实例必须在组件卸载时销毁，不能把外部脚本地址当作动画数据。
- 文件扩展名和 MIME 检查只能改善体验，不能替代后端文件安全校验。

## 类型、样式和页面目录

- 所有 `type`、`interface`、`enum` 声明必须位于 `src/types/`；页面、组件、Hook、Store、Router 和工具文件只能通过 `@/types` 导入声明，不得创建页面内 `types.ts`。
- 新增样式优先使用 UnoCSS utility class。只有组件专属复杂选择器、伪元素、关键帧、CSS 变量或第三方覆盖才允许新增 `<style scoped>` 规则。
- `src/views/` 下目录名必须语义化、可从名称判断业务域或页面职责，并与后端路由 `component` 路径保持一致；禁止使用无意义的通用目录或缩写。

## 依赖与生成物

- 优先复用现有 Vue、Pinia、Vue Router、Alova、Naive UI 和工具链。
- 新依赖必须说明必要性、体积和安全影响，并同步 `package.json` 与锁文件；不可依赖未声明的传递依赖。
- `auto-imports.d.ts`、`components.d.ts`、`dist*` 等生成文件不能手工修改来掩盖源码问题。
- 依赖升级、全量格式化、文件重命名和生成物清理不属于普通功能任务范围。

## 偏好与双语边界 / Preference and bilingual boundary

- `usePreferencesStore` 只保存非敏感的界面偏好；不得把 Token、密码、验证码、MFA、刷新令牌或业务数据加入偏好快照、复制内容或水印。
- `zh-CN` / `en-US` 只改变前端界面文案和已知静态路由标题，不改变后端请求字段、权限码、状态枚举、业务数据或错误契约。
- 后端动态菜单标题没有词典映射时必须保留原文，不能根据文案猜测权限或强行翻译成错误含义。
- `autoUpdate` 当前是可持久化的 UI 开关，不代表已经存在更新服务；新增更新请求前必须先核对真实 endpoint、响应、权限、缓存和失败处理。
- 内容区三种滚动模式只能改变布局滚动容器和 sticky 行为，不得影响路由守卫、KeepAlive、菜单权限或 API 调用。
