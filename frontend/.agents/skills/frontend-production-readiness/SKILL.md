---
name: frontend-production-readiness
description: 评审或改进 Vue/Vite 管理端的生产构建、静态资源、运行配置、版本清单、部署基础路径、API 代理边界、安全暴露和发布风险。修改 frontend/vite.config.ts、环境样例、构建脚本、发布配置或进行前端发布评审时使用。
---

# Frontend 生产就绪性

用于发布和运行时评审，必须将代码检查、构建结果、部署配置、真实 API 和浏览器验证分别报告。

## 工作流程

1. 变更前确认目标环境、授权与外部影响；不得将真实服务 URL、Token、密钥或生产配置写入
   `.env` 样例、日志、测试或文档。
2. 检查 `package.json`、`vite.config.ts`、环境样例、入口、请求层、版本清单、静态资源和部署
   相关配置，确认 Node/pnpm 约束与脚本一致。
3. 核实构建行为：`VITE_BASE_PATH`、构建输出、分块策略、source map、压缩、`version.json`、
   静态资源路径、路由回退和缓存失效策略。
4. 核实运行边界：开发代理只用于开发；生产 API 来源、CORS、认证 Cookie/Token、错误反馈、
   下载、外链和上传不依赖本地代理或 Debug 行为。
5. 检查供应链与安全：不新增无必要依赖；不暴露敏感环境值；不使用不受控 iframe、外链、
   动态 import 路径、`v-html` 或生产 Mock。
6. 执行逐级验证：

```powershell
pnpm run check
pnpm run build
git diff --check
```

7. 只有在目标部署和真实后端已明确可用时，才进行部署、浏览器或真实 API 验证；分别报告
   未执行项与剩余风险。

## 发布门禁

- 本地构建通过不代表 CDN、Nginx、路由回退、浏览器缓存、真实认证或后端 API 已验证。
- 生产构建不依赖 `VITE_API_PROXY_TARGET` 的开发代理。
- 未核验基础路径、运行时 API、认证和版本清单时，不得声称可以发布。

详细检查项见 [release-checklist.md](references/release-checklist.md)。
