---
name: frontend-code-review
description: 以代码评审方式检查 Vue 管理端具体缺陷、认证和权限体验回归、接口契约漂移、路由布局问题、状态持久化风险、可访问性问题、构建故障与测试缺口。用户要求 review、审计、发布风险检查或只读评估 frontend 改动时使用。
---

# Frontend 代码评审

默认只读。优先发现会造成敏感信息泄露、越权体验误导、请求契约错误、路由不可达、运行失败、
用户数据错用或发布阻塞的问题。

## 工作流程

1. 确认评审范围和基线；用户未指定时，读取当前工作区差异，不擅自扩大到整个提交历史。
2. 读取仓库与前端规则，以及改动涉及的类型、API/Parser、Store、路由、布局、组件、样式和
   测试；必要时读取实际后端 Controller/DTO 契约。
3. 沿真实调用链检查：页面/布局 → Store 或交互编排 → API/Parser → 请求层 → 路由/权限/反馈。
4. 按优先级检查：
   - Token、密码、验证码、MFA、敏感响应、XSS、外链、iframe、动态 import 和浏览器存储。
   - API 方法、路径、字段、分页、空值、错误、下载上传、租户与权限体验同后端契约的偏差。
   - 守卫、动态路由、路由缓存、标签、Loading、系统设置抽屉和布局内容区的状态回归。
   - `any`、未验证断言、传输层绕过、重复 Store/API/组件方案、不可访问图标按钮和无效 UI 状态。
   - Vite 输出、资源路径、版本清单、测试覆盖和 Windows `spawn EPERM` 环境边界。
5. 每项发现给出文件/行号、严重级别、可复现路径、实际影响、根因和最小修复方向；区分确定
   缺陷、能力缺失与未验证风险。
6. 只运行不改变状态的验证，例如目标测试、静态搜索、`pnpm run check` 或 `git diff --check`，
   并说明浏览器、真实 API 和部署验证是否未执行。

## 输出顺序

1. Findings：按严重性从高到低，附文件/行号和证据。
2. Open questions / assumptions：只列影响结论的事项。
3. Change summary：简述实际范围。
4. Test gaps / residual risk：列出未执行的浏览器、真实后端与部署验证。

详细检查项见 [review-checklist.md](references/review-checklist.md)。
