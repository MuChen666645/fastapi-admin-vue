# 前端工作流和验证规则

## 任务分类

开始修改前先判断任务属于缺陷修复、功能开发、接口变更、重构、安全修复或规则文档维护。规则文档任务必须以当前源码、依赖和测试为事实来源，不能把历史摘要当作已实现能力。

## 修改前检查

1. 读取仓库根目录 `AGENTS.md`、`frontend/AGENTS.md` 和 `.codex/` 核心文件。
2. 检查 `git status --short`，保留用户已有修改，不覆盖或回滚无关文件。
3. 使用 `rg` 查找目标调用方、接口路径、类型、图标导入、路由名称、Store 和测试。
4. 检查 `package.json`、`pnpm-lock.yaml` 和实际安装目录，确认依赖名称，不凭记忆写包名。
5. 需要接口时阅读后端 Controller、DTO、Service、配置和对应测试，记录方法、完整路径、编码、响应、错误、权限和租户字段。
6. 需要模块迁移时先画出依赖关系，明确旧入口、兼容出口、目标模块和调用方迁移顺序。

## 模块化实现要求

### 类型

- 先在 `src/types/` 独立领域文件中定义请求、响应、表单、状态和路由类型。
- 类型按领域拆分，并通过领域 `index.ts` 和 `src/types/index.ts` 统一导出。
- API 运行时解析器与类型声明分离；解析器接收 `unknown`，不得直接把响应断言成目标类型。
- API 层保留后端蛇形字段，页面显示字段转换必须由命名明确的适配器完成。

### 图标

- 所有功能图标从 `@vicons/ionicons5` 静态导入；禁止混用其他图标库、手写 SVG、Emoji 和 Unicode 符号。
- `@vicons/utils` 只作为图标包装工具。当前依赖未声明时，不得直接导入，先完成依赖评审和锁文件更新。
- 图标按钮补充 `aria-label`、`title`、加载和禁用状态；装饰图标使用 `aria-hidden`。

### API

- API 按业务领域放入 `src/api/<domain>/index.ts`，响应解析放入对应 `parsers.ts` 或 `src/utils/guards/`。
- `src/api/index.ts` 提供唯一公共出口；调用方从 `@/api` 导入，禁止绕过出口引用深层实现文件。
- `src/utils/request.ts` 集中处理基地址、鉴权头、响应解包、错误归一化、超时和 401 单飞刷新。
- API 模块不负责页面展示、路由跳转、Store 实例化和权限猜测。

### 路由

- 路由按领域放入 `src/router/modules/`，守卫放入 `src/router/guards/`，分别通过 `index.ts` 汇总。
- `src/router/index.ts` 只负责创建 Router、安装模块和守卫，并导出公共路由能力。
- 动态路由必须经过运行时校验和本地组件白名单，不得执行服务端字符串导入。

### Store

- Store 按领域放入 `src/stores/modules/`，每个 Store 只管理一个领域，通过 `src/stores/index.ts` 统一导出。
- Store 可以调用 `@/api`，但不复制响应解析、不操作 DOM、不依赖页面组件、不保存服务端密钥。
- 持久化字段必须显式列出，默认不持久化 Token、密码、验证码、MFA、密码重置令牌和敏感用户数据。

## 实现顺序

1. 定义类型和运行时校验边界。
2. 在领域 API 模块实现接口并接入统一出口。
3. 在 Store 或 composable 中编排状态、加载、取消、错误和重试。
4. 在路由模块中声明页面路由，在守卫模块中处理认证和动态路由。
5. 页面只处理展示、表单交互和页面级编排。
6. 使用 Ionicons 5 完成功能图标，并补齐可访问名称和状态。
7. 覆盖成功、空数据、参数错误、401、403、限流、网络失败、重复提交和取消状态。
8. 迁移旧入口调用方，确认统一出口没有循环依赖和同名覆盖。

## 规则文档维护顺序

当依赖、目录职责或架构约束发生变化时：

1. 先核对源码、`package.json` 和锁文件。
2. 更新 `PROJECT.md` 的已核实事实。
3. 更新 `ARCHITECTURE.md` 的目标结构和依赖方向。
4. 更新 `BOUNDARY.md` 的安全边界和禁止事项。
5. 更新 `AGENTS.md` 的强制执行规则。
6. 更新本文件和任务模板中的执行顺序。
7. 检查 README、示例和旧规则入口是否出现第二套约定。

## 验证命令

在 `frontend/` 目录按顺序执行：

```text
pnpm run type-check
pnpm run lint
pnpm run lint:style
pnpm run format:check
pnpm run test:unit -- --run
pnpm run build
```

构建验证优先使用已知临时输出目录，避免污染 `dist/`；验证后只清理本次创建的临时目录。Windows 上如果 Vite/Vitest 因 `spawn EPERM` 无法启动，应在允许子进程的环境重试，并分别报告源码检查和运行时检查结果。

交付前执行：

```text
git diff --check
git status --short
```

## 交付报告

使用中文说明：

```text
完成结果：
修改文件：
当前事实和设计决策：
模块化和统一出口影响：
接口、路由、Store 和图标影响：
验证命令及结果：
未完成验证及原因：
剩余风险：
```
