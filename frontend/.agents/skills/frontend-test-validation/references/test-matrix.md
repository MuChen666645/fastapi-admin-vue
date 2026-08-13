# 前端测试矩阵

| 变更范围                   | 首选验证                                 | 需要扩大时                               |
| -------------------------- | ---------------------------------------- | ---------------------------------------- |
| API、Parser、类型          | 对应 `*Api.spec.ts`、`ApiTypes.spec.ts`  | 请求层与调用组件测试                     |
| Store、偏好、字典、消息    | 对应 Store 测试                          | 会话/路由/布局测试                       |
| 登录、Token、守卫、权限    | Auth API/Store/Guard/Directive/Hook 测试 | Request、DynamicRouter、BasicLayout 测试 |
| 路由、标签、缓存、Loading  | Route/Tab/Cache/BasicLayout 测试         | `pnpm run build`                         |
| 路由页面与表单交互         | 对应页面/组件测试                        | API、权限、布局相邻测试                  |
| Vite、资源、入口或公共样式 | `pnpm run check`                         | `pnpm run build`                         |

## 结果分类

- `通过`：命令实际运行且退出成功。
- `失败`：命令实际运行但存在可复现失败。
- `未执行`：因环境、权限或外部依赖未运行。
- `未覆盖`：当前验证没有触及该行为，不能描述为通过。
