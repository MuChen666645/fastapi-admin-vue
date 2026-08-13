# 前端 API 契约检查表

## 请求与类型

- [ ] 已从真实后端 Controller、DTO 和测试核对 `/api/v1` 路径、方法与字段。
- [ ] Query、Path、Body、FormData、分页和排序参数没有遗漏或错用 UI 字段名。
- [ ] API 类型保留服务端蛇形字段，并从 `src/types/` 统一导出。
- [ ] 页面、Store 和 Router 没有定义重复的领域 API 类型。

## 解析与调用

- [ ] `src/api/<domain>/index.ts` 只负责请求编码，`parsers.ts` 校验响应结构。
- [ ] 使用 `requestJson`、`requestBlob` 或已有请求封装，没有新建平行传输层。
- [ ] null、空列表、分页元数据、文件流和业务错误语义明确。
- [ ] 全部真实调用方的列表、详情、提交、删除、刷新和错误反馈已检查。

## 验证

- [ ] API/Parser 测试覆盖请求载荷和响应解析。
- [ ] 契约变化已同步检查后端和前端调用方。
- [ ] 已运行目标测试、`pnpm run check` 与 `git diff --check`。
