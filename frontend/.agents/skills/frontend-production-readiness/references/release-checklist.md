# 前端发布检查表

## 构建与资源

- [ ] Node、pnpm、Vite 脚本和输出目录与当前 `package.json`、`vite.config.ts` 一致。
- [ ] 基础路径、代码分块、静态资源、`version.json`、压缩和 source map 配置已核对。
- [ ] 构建输出不是提交内容，构建过程没有修改源码或生成声明。

## 运行边界

- [ ] 生产运行不依赖开发 Vite proxy。
- [ ] API 来源、CORS、认证、路由回退、缓存与版本更新策略已和部署方核对。
- [ ] 下载、上传、外链、iframe 和错误处理没有泄露敏感数据或产生不受控导航。

## 验证结果

- [ ] `pnpm run check` 和 `pnpm run build` 实际通过。
- [ ] 浏览器、真实 API、部署、CDN/Nginx 和生产认证验证分别记录。
- [ ] 未执行项和发布风险明确列出。
