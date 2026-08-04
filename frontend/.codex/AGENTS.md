# 前端 Codex 核心规则

本文件是 `frontend/.codex/` 的强制实现规则。它约束代码组织、安全边界和验证方式，不替代当前源码、测试、构建配置或后端接口契约。

## 规则加载

修改前端文件前按以下顺序读取：

1. 仓库根目录 `AGENTS.md`。
2. `frontend/AGENTS.md`。
3. 本文件。
4. `PROJECT.md`、`ARCHITECTURE.md`、`BOUNDARY.md`、`WORKFLOW.md`。
5. 与任务对应的 `PROMPTS/feature.md` 或 `PROMPTS/bugfix.md`。

## 必须遵守

- 使用 Vue 3 Composition API、`<script setup lang="ts">`、TypeScript strict、Pinia、Vue Router、Alova 和 Naive UI；不在未评审时引入同类框架或 HTTP 客户端。
- 所有请求经过 `src/api/<domain>/index.ts` 和 `src/utils/request.ts`。页面和 Store 不得直接访问 Alova、`fetch`、Axios 或服务端 URL。
- API 响应先由 `parsers.ts` 接收 `unknown` 并校验，再交给业务层；禁止用类型断言绕过校验。
- 所有 production 和 test 中的 `type`、`interface`、`enum` 声明都放在 `src/types/` 的语义化领域文件中，并通过 `@/types` 统一出口导出；页面、组件、Hook、Store、Router 和工具文件只允许导入类型，不允许声明类型。
- 编写样式时优先使用 UnoCSS utility class。`<style scoped>` 仅用于组件专属复杂选择器、伪元素、关键帧、CSS 变量和第三方样式覆盖；不要为普通布局、间距、颜色和响应式规则新增重复 CSS。
- `src/views/` 下的目录名必须语义化并描述业务域或页面职责，使用现有的小写 kebab-case 约定；禁止 `page`、`view`、`temp`、`common`、`misc`、数字和无意义缩写。页面业务组件放到对应页面的 `components/`，跨页面复用组件放到 `src/components/`。
- 路由模块只声明路由，守卫只处理认证和安全重定向，动态路由只从本地 View 白名单解析。
- Store 只管理跨页面状态和动作，不访问 DOM、不依赖页面组件、不保存服务端密钥。
- 功能图标统一从 `@vicons/ionicons5` 静态导入；按钮必须有可访问名称，装饰图标必须 `aria-hidden`。
- 不写入真实密钥、Token、密码、验证码、MFA、生产数据、临时日志或生成物。
- 不用假数据、静默 Mock、`any`、`@ts-ignore`、无检查断言或放宽权限来掩盖问题。
- 可复用组件或组件组必须在所属目录维护 `README.md`；文档至少说明用途边界、Props、Emits、Slots、暴露方法、校验/状态约定和最小使用示例，并与源码和测试同步更新。
- 组件文档中的提交示例必须通过页面的 `@submit` 调用 `@/api`，组件本身只负责展示、交互和校验，不得把业务请求写入通用组件。

## 当前路由事实

- `src/router/index.ts` 创建 Router、注册静态路由和认证守卫，并暴露动态路由注册/清理能力。
- `src/router/modules/public.ts` 提供双语登录页，`protected.ts` 提供认证入口、修改密码页、`system-settings` 和“演示 / 功能 / 表单、搜索表单、缺省页 / 403、404、500、网络离线”静态菜单树，`error.ts` 提供 403、404、500 和离线页面。
- 认证后通过 `GET /api/v1/user/routes` 获取业务路由，并将通过校验的路由添加到 `app` 布局下。
- 项目不再使用 `VITE_ROUTE_MODE`，不再维护前端静态业务路由清单。

## 当前状态事实

- `auth` Store 管理 Token、当前用户、权限、后端路由和初始化状态；仅持久化刷新 Token 与记住的用户名。
- `tabs` Store 使用 `sessionStorage` 持久化标签页；`route-loading` Store 管理 `screen`/`content` 两种 Loading 范围，并保持最短可见时间。
- `BasicLayout` 将内容区 Loading、标签页、面包屑、KeepAlive 和路由页面组合在一起。
- Lottie 封装位于 `src/utils/lottie.ts` 和 `src/hooks/useLottie.ts`，动画组件使用 `src/assets/lottie/car-loading3-data.json`。

## 维护规则

当确认了 API、路由、权限、依赖、目录职责、缓存或构建脚本变化时，必须同步更新 `PROJECT.md`、`ARCHITECTURE.md`、`BOUNDARY.md` 或 `WORKFLOW.md` 中受影响的事实。文档不得保留已经删除的路径、变量、脚本或兼容分支。

新增可复用组件时，必须同时检查组件目录的 `README.md`、`src/types/` 类型出口、组件级测试和必要的静态演示路由；仅新增源码而没有使用文档或验证用例不视为完整交付。
