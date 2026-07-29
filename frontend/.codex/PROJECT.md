# 前端项目事实

本文件只记录已从当前工作区和 `service/` 源码核对出的事实。目标目录结构属于实现规则，不得把目标结构误写成当前已完成状态。

## 项目定位

`frontend/` 是与 FastAPI 管理服务通过 HTTP 契约协作的 Vue 3 单页应用，使用 TypeScript、Vite、Vue Router、Pinia、Alova、Naive UI 和 UnoCSS reset。

当前认证和管理基础能力已存在，但部分目录仍是过渡结构：

```text
src/api/auth.ts          # 当前认证接口聚合文件
src/router/index.ts      # 当前静态路由、守卫和动态路由注册入口
src/router/dynamic.ts    # 当前动态路由转换
src/stores/auth.ts       # 当前会话 Store
src/types/api.ts         # 当前 API 类型和部分运行时解析器
src/types/router.d.ts    # 当前路由元信息类型扩展
```

新功能必须遵循模块目录和统一出口规则；迁移上述旧入口时必须保留兼容行为并同步迁移调用方和测试。

## 技术和依赖事实

- 包管理器是 pnpm，必须使用 `frontend/pnpm-lock.yaml`。
- `package.json` 声明 Node 版本为 `^22.18.0 || >=24.12.0`。
- 已声明的图标依赖是 `@vicons/ionicons5`，当前未声明 `@vicons/utils`。
- 统一图标规范使用 Ionicons 5；若需要使用 `@vicons/utils` 的 `Icon` 包装器，必须先将它作为直接依赖声明并更新锁文件。
- `src` 的路径别名是 `@`，指向 `src`。
- `tsconfig.app.json` 启用 `noUncheckedIndexedAccess`，新代码不得降低严格性。
- 质量脚本包括 `pnpm run type-check`、`pnpm run lint`、`pnpm run lint:style`、`pnpm run format:check`、`pnpm run test:unit -- --run` 和 `pnpm run build`。

## 目标模块结构

新增或迁移领域代码按以下结构组织：

```text
src/
├── api/
│   ├── auth/index.ts
│   ├── user/index.ts
│   └── index.ts
├── router/
│   ├── modules/index.ts
│   ├── guards/index.ts
│   └── index.ts
├── stores/
│   ├── modules/index.ts
│   └── index.ts
└── types/
    ├── api/index.ts
    ├── router.ts
    └── index.ts
```

每层的 `index.ts` 是统一出口，只做显式导出，不保存业务状态、不执行请求、不创建 Router/Pinia 实例、不安装插件，也不产生导航副作用。

## 前端接口事实

- 默认 API 前缀由后端 `API_V1_PREFIX` 控制，当前为 `/api/v1`。
- JSON 响应通常由 `ResponseInterceptor` 包装为 `{ code, error_code?, message, data }`。
- 登录接口为 `POST /api/v1/user/login/username` 和 `POST /api/v1/user/login/phone`，当前使用表单编码，字段包括 `captcha_id`、`captcha`、用户名或手机号、`password` 和可选 `mfa_code`。
- 图形验证码为 `GET /api/v1/captcha/image`，请求需要防缓存时间戳。
- 刷新令牌为 `POST /api/v1/user/token/refresh`，退出为 `POST /api/v1/user/logout`。
- 当前用户信息为 `GET /api/v1/user/info`，动态路由为 `GET /api/v1/user/routes`。
- 令牌字段包括 `access_token`、`refresh_token`、`token_type`、`expires_in` 和 `must_change_password`。
- 密码找回接口为 `POST /api/v1/user/password/forgot` 和 `POST /api/v1/user/password/reset`，字段和响应必须以当前后端 DTO、Controller、Service 和测试为准。
- 文件上传、下载、导出和流式接口可能返回原始二进制，不能强行套用 JSON 解包。

## 后端权威边界

- 后端负责认证、授权、租户、数据范围、字段权限、业务状态和数据一致性。
- 前端路由守卫、权限指令、隐藏菜单和禁用按钮只改善体验，不能代替后端校验。
- API 响应、服务端菜单、外部链接、上传信息和查询参数都必须经过边界验证后才能进入业务层。

## 事实更新规则

涉及 API 字段、路由、依赖、图标包、鉴权、文件、分页、构建工具或目录职责时，必须重新检查对应源码、`package.json`、锁文件、后端 Controller、DTO、配置和测试。不要仅凭历史文档生成接口、字段、权限或依赖名称。
