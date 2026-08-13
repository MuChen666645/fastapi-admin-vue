---
name: frontend-test-validation
description: 为 Vue 管理端选择并执行 API、Parser、Store、路由、权限、布局、组件、构建和静态检查验证；诊断 Vitest、TypeScript、ESLint、Stylelint、Prettier 或 Vite 失败，并如实报告验证边界时使用。
---

# Frontend 测试验证

用于按变更风险选择最小有效验证，并明确区分静态检查、Vitest、构建、浏览器和真实后端联调。

## 工作流程

1. 记录当前工作区状态和改动层次，不覆盖用户的无关修改。
2. 以行为和契约选择目标测试：API/Parser、Store、守卫、权限指令、布局、页面交互或工具函数；
   不以仅验证源码文本或实现细节替代行为测试。
3. 对共享边界扩大范围：请求层、认证、动态路由、BasicLayout、全局 Loading、类型出口、构建
   配置和可复用组件变更都应补充相邻回归测试。
4. 运行 `pnpm exec vitest run <tests>`、`pnpm run check` 和 `git diff --check`；影响生产构建、
   公共资源或 Vite 配置时运行 `pnpm run build`。
5. 从第一条失败输出定位原因，不通过更改断言、放宽类型、关闭 lint 或跳过测试掩盖缺陷。
6. Windows 上出现 `spawn EPERM` 时，区分配置加载子进程失败与源码校验结果；仅在允许子进程
   的环境重试，并如实报告。
7. 分别报告已通过、失败、未执行和未覆盖项目。Vitest 与构建不证明浏览器交互、真实 FastAPI、
   登录、Redis 或 MySQL 联调完成。

详细测试选择见 [test-matrix.md](references/test-matrix.md)。
