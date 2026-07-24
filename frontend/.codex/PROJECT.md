# 前端项目事实

本文件记录从当前工作区和 service 项目核对出的事实，是前端代码生成时的项目上下文。任务依赖可能变化的细节时，必须重新检查源码。

## 项目定位

frontend 是与 FastAPI 管理服务配套的 Vue 3 单页应用。当前前端仍处于基础模板阶段，不应假设已经存在完整的登录页、布局、API 客户端、鉴权 Store 或动态路由加载器。

## 技术栈和脚本

- Vue 3、Composition API、TypeScript、Vite。
- Vue Router、Pinia、Alova。
- Naive UI、UnoCSS reset、SVG 加载插件。
- Vitest、Vue Test Utils、jsdom、vue-tsc、Prettier。
- 包管理器是 pnpm，必须使用已提交的 pnpm-lock.yaml。
- package.json 声明 Node 版本为 ^22.18.0 或 >=24.12.0。
- 类型检查命令：pnpm type-check。
- 单元测试命令：pnpm test:unit -- --run。
- 生产构建命令：pnpm build。
- 格式化命令：pnpm format。
- src 的路径别名是 @，指向 src。
- tsconfig.app.json 启用 noUncheckedIndexedAccess；新代码不得降低严格性。

## 当前源码

当前已确认的源码包括：

~~~text
src/App.vue
src/main.ts
src/router/index.ts
src/stores/counter.ts
src/__tests__/App.spec.ts
~~~

当前路由表为空，示例 Store 不是业务会话 Store，不能将模板代码当作成熟架构直接复制。

## 后端接口事实

- 默认 API 前缀是 /api/v1，由 service/config/env.py 的 API_V1_PREFIX 控制。
- JSON API 通常由 ResponseInterceptor 包装为 code、error_code、message、data。
- 登录接口是 POST /api/v1/user/login/username 和 POST /api/v1/user/login/phone，当前使用表单编码。
- 登录字段包括 captcha_id、captcha、用户名或手机号、password，以及可选 mfa_code。
- 图形验证码接口是 GET /api/v1/captcha/image；旧的数字验证码接口已经停用并返回 410。
- 刷新令牌接口是 POST /api/v1/user/token/refresh。
- 退出登录接口是 POST /api/v1/user/logout。
- 当前用户信息接口是 GET /api/v1/user/info。
- 当前用户动态路由接口是 GET /api/v1/user/routes。
- 令牌字段包括 access_token、refresh_token、token_type、expires_in、must_change_password。
- 动态路由字段包括 path、name、component、redirect、hidden、meta、children。
- 列表接口通常使用 fastapi-pagination 的分页结构，必须以具体 DTO 和实际响应为准。
- 文件上传、下载、导出和流式接口可能返回原始二进制，不能套用 JSON 解包。
- 后端权限编码、租户过滤、字段权限和数据范围是服务端强制控制，前端不能自行放宽。

## 后端架构事实

后端主要分层为：

~~~text
Controller -> Service -> DAO -> Database
~~~

- Controller 负责路由、参数、依赖和响应声明。
- Service 负责业务规则、权限、租户、数据范围、幂等和外部服务编排。
- DAO 负责 SQL 查询、分页和持久化。
- entity/dto 是外部 API 合同，entity/do 是数据库模型。
- 业务 HTTP 请求使用 request.state.mysql。
- 审计、迁移、调度、导出、通知和独立 Worker 使用 app.state.mysql_session_factory 或明确的独立会话工厂。
- Redis 是 app.state.redis 上的共享客户端，不是请求级客户端。

## 事实更新规则

涉及接口字段、路由、鉴权、文件、分页、构建工具或依赖时，必须重新阅读对应的 service 控制器、DTO、配置和测试。不要仅凭本文件生成接口。
