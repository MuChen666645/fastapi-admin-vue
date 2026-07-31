# frontend

## 环境变量

复制 `.env.example` 为 `.env.local`，再按运行环境修改。Vite 只会把 `VITE_*` 变量注入前端，因此这些变量只能保存浏览器可公开读取的配置，不能填写密码、Token、签名密钥或内部服务凭据。

常用变量：

- `VITE_API_BASE_URL`：前端 API 基础路径，默认 `/api/v1`。
- `VITE_API_PROXY_TARGET`：开发代理目标，默认 `http://127.0.0.1:3000`。
- `VITE_API_PROXY_ENABLED`：是否启用开发代理；预发布和生产默认关闭。
- `VITE_DEV_HOST`、`VITE_DEV_PORT`、`VITE_DEV_OPEN`：Vite 开发服务器配置。
- `VITE_PREVIEW_HOST`、`VITE_PREVIEW_PORT`：`vite preview` 服务配置。
- `VITE_BASE_PATH`：部署在子路径时的静态资源基础路径，默认 `/`。
- `VITE_SOURCEMAP`：是否生成 sourcemap，默认关闭。

开发环境默认代理 `/api/*` 到 FastAPI 的 `http://127.0.0.1:3000`，保留 `/api/v1` 前缀。生产环境应由 Nginx 或其他网关代理 `/api`，不要把容器内部地址写入浏览器环境变量。

路由统一从后端 `/user/routes` 获取。后端路由的 `component` 会在前端静态 `src/views/**/*.vue` 映射中解析，支持 `home/index`、`@/views/home/index.vue` 和 `../views/home/index.vue` 等形式。未找到本地组件的路由不会注册，并会在控制台输出警告。

Vite 环境文件按 mode 加载：`.env` 保存公共配置，`.env.development` 用于开发，`.env.staging` 用于预发布，`.env.production` 用于生产；对应的 `.local` 文件可覆盖本机配置且不会提交。单元测试使用 Vitest 内置的 `test` mode，不维护 `.env.test`。

常用命令：

```sh
pnpm dev                 # 开发运行
pnpm dev:staging         # 预发布运行
pnpm build               # 生产打包到 dist/
pnpm build:staging       # 预发布打包到 dist-staging/
pnpm preview             # 预览生产构建
pnpm preview:staging     # 预览预发布构建
pnpm test:run            # 运行单元测试
```

`dev`、`build`、`preview` 和 `test` 入口都会先运行 `pnpm run check`，依次执行类型检查、ESLint、Stylelint 和 Prettier 格式检查。提交时由 `lint-staged` 对暂存文件执行自动修复。

This template should help get you started developing with Vue 3 in Vite.

## Recommended IDE Setup

[VS Code](https://code.visualstudio.com/) + [Vue (Official)](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (and disable Vetur).

## Recommended Browser Setup

- Chromium-based browsers (Chrome, Edge, Brave, etc.):
  - [Vue.js devtools](https://chromewebstore.google.com/detail/vuejs-devtools/nhdogjmejiglipccpnnnanhbledajbpd)
  - [Turn on Custom Object Formatter in Chrome DevTools](http://bit.ly/object-formatters)
- Firefox:
  - [Vue.js devtools](https://addons.mozilla.org/en-US/firefox/addon/vue-js-devtools/)
  - [Turn on Custom Object Formatter in Firefox DevTools](https://fxdx.dev/firefox-devtools-custom-object-formatters/)

## Type Support for `.vue` Imports in TS

TypeScript cannot handle type information for `.vue` imports by default, so we replace the `tsc` CLI with `vue-tsc` for type checking. In editors, we need [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) to make the TypeScript language service aware of `.vue` types.

## Customize configuration

See [Vite Configuration Reference](https://vite.dev/config/).

## Project Setup

```sh
pnpm install
```

### Compile and Hot-Reload for Development

```sh
pnpm dev
```

### Type-Check, Compile and Minify for Production

```sh
pnpm build
```

### Run Unit Tests with [Vitest](https://vitest.dev/)

```sh
pnpm test:run
```

## 设计稿关联

- Pixso 设计文件：https://pixso.cn/app/design/uzGAyjde0EOwEse-BkB2Ug?icon_type=1&page-id=4%3A11257
- 关联前端模块：`src/layouts/BasicLayout/components/AppSidebar/index.vue`
