# 前端项目上下文

本文件记录从当前工作区核对过的事实。任务依赖可能变化的细节时，必须重新检查源码。

## 当前前端

- 项目位置：`E:/fastapi-admin-vue/frontend`。
- 技术栈：Vue 3、Vite、TypeScript、Vue Router、Pinia、Alova、Naive UI、Vitest 和 Prettier。
- 包管理器：pnpm，仓库提交了 `pnpm-lock.yaml`。
- `package.json` 声明的 Node 版本：`^22.18.0 || >=24.12.0`。
- 当前源码仍是基础模板：`src/App.vue`、`src/main.ts`、空路由表、示例 Pinia Store 和一个基础单元测试。
- `@` 别名指向 `src`。
- 类型检查使用 `vue-tsc --build`，并启用 `noUncheckedIndexedAccess`。
- 当前没有默认存在的 API 客户端、鉴权 Store、动态路由加载器或应用布局，开发前必须先确认实际文件。

## 前端使用的后端事实

- FastAPI 服务默认 API 前缀为 `/api/v1`。
- JSON API 响应格式为 `{ code, error_code, message, data }`。
- 登录接口为 `/user/login/username` 和 `/user/login/phone`，当前接收表单编码数据。
- 登录数据包含 `captcha_id` 和 `captcha`，验证码图像和校验接口位于 `/captcha` 下。
- 令牌数据包含 `access_token`、`refresh_token`、`token_type`、`expires_in` 和 `must_change_password`。
- 刷新接口为 `/user/token/refresh`；退出登录为 `/user/logout`；当前用户信息为 `/user/info`；动态路由为 `/user/routes`。
- 动态路由对象包含 `path`、`name`、`component`、`redirect`、`hidden`、`meta` 和 `children`。
- 敏感读取、写入、导出、下载和文件操作必须由后端权限保护；前端权限判断只负责控制显示和导航。
- 文件下载、导出以及部分文件接口有意返回非 JSON 响应，必须跳过统一 JSON 解包。

## 当前工作假设

- 除非经过评审的契约变更明确要求，否则后端字段保持蛇形命名。
- 前端公开环境变量只保存配置，任何浏览器可见变量都不能视为密钥。
- 新增 API 层时优先使用现有 Alova，不另行引入 HTTP 客户端。
- 动态路由组件必须映射到本地文件白名单。

## 更新规则

如果任务涉及鉴权、路由、文件处理、API 响应格式或构建工具，必须重新检查对应的后端 DTO 和控制器。确认新契约后才能更新本文件；本文件过期时，以源码和已验证契约为准。
