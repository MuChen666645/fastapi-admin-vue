# 前端缺陷修复模板

维护目录：`E:/fastapi-admin-vue/frontend`

开始前阅读：仓库根目录 `AGENTS.md`、`frontend/AGENTS.md`、`.codex/AGENTS.md`、`.codex/PROJECT.md`、`.codex/ARCHITECTURE.md`、`.codex/BOUNDARY.md` 和 `.codex/WORKFLOW.md`。

## 缺陷输入

```text
现象：
复现步骤：
预期结果：
实际结果：
错误信息或截图：
影响页面、路由、Store 或接口：
```

## 修复要求

1. 先读取真实组件、布局、路由守卫、Store、hook、API parser 和现有测试，复现后再判断根因。
2. 区分展示层、页面状态、Pinia 状态、传输层、动态路由、KeepAlive、Loading 生命周期和后端契约问题。
3. 涉及接口时只读核对后端 Controller、DTO、配置和测试；默认不修改 `service/`。
4. 说明触发条件和根因，实施最小且可维护的修复，不用 `any`、`@ts-ignore`、假数据、放宽安全校验或静默兜底掩盖问题。
5. 动态路由仍只能从本地 View 白名单解析；未知组件应过滤并警告，不能直接导入服务端字符串。
6. 为回归路径补充专项测试，至少覆盖修复成功路径以及相关的错误、空值、未授权、重复导航或竞态状态。
7. 如果涉及 KeepAlive，分别证明组件缓存行为和 tabs 列表持久化行为；如果涉及 Loading，分别验证布局外全屏和布局内内容区范围。
8. 检查 XSS、令牌泄露、越权误导、无限重试、重复请求、Lottie 实例泄漏和对象 URL 泄漏风险。

9. 修复过程中不得在页面、组件、Hook、Store、Router 或工具文件内新增类型声明；类型统一放入 `src/types/`。新增样式优先使用 UnoCSS，并保持 `views` 目录语义化。

## 验证命令

```text
pnpm run check
pnpm run test:run
pnpm run build
git diff --check
```

Windows 下若 Vite/Vitest 因 `spawn EPERM` 无法启动，使用允许子进程的环境重试，并分别报告静态检查和运行时测试结果。

## 交付报告

```text
根因：
修改：
回归风险：
安全影响：
验证：
未完成验证及原因：
涉及文件：
剩余风险：
```
