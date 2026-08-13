# 跨端验证矩阵

| 变更范围                 | 首选验证                                           | 扩大验证                           |
| ------------------------ | -------------------------------------------------- | ---------------------------------- |
| 前端 API/Parser          | 对应 Vitest API 测试、`pnpm run check`             | 调用页面与请求层测试               |
| 后端 DTO/Controller      | 对应 pytest 模块测试、compileall                   | API/安全回归测试                   |
| 认证、权限、租户         | 前端 Store/Guard/Directive 与后端授权测试          | Redis/MySQL 集成验证               |
| 路由、布局、Loading      | 前端路由/BasicLayout 测试                          | `pnpm run build`、浏览器验证       |
| 迁移、seed、schema       | pytest 迁移/SQL 测试、`alembic upgrade head --sql` | 真实 MySQL 升级                    |
| Worker、调度、通知、导出 | Service 单元测试                                   | Redis/MySQL/Worker 集成            |
| 运行和发布               | 前后端静态检查与构建                               | Docker、浏览器、真实 API、目标环境 |

`通过` 表示命令实际退出成功；`未执行` 表示没有运行；`未覆盖` 表示当前验证未触及；`失败` 表示存在可复现失败。
