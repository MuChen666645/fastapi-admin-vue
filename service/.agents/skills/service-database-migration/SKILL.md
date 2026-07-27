---
name: service-database-migration
description: 设计、实现、评审和验证 SQLModel/Alembic/MySQL schema 变更、索引、约束、初始化 SQL、数据回填和权限 seed。修改 module_admin/entity/do、alembic/versions、assets/sql、数据库配置或迁移编排时使用。
---

# Service 数据库迁移

用于让 schema 变更可审阅、可升级、可回滚或明确说明不可回滚，并同步 DO/DTO、DAO、Service、权限 seed 和测试。

## 工作流程

1. 明确表、字段、可空性、默认值、精度、索引、唯一约束、外键、权限 seed、租户键、所有权和数据回填要求。以当前迁移 head 和模型为准，不假设版本号。
2. 判断变更应放在 Alembic、`assets/sql/fastapi-admin.sql`、`assets/sql/schema-upgrade.sql`，还是需要同步更新。Web 启动不能承担不可重复的 schema 修复。
3. 模型和迁移同时更新时，保持 DO 与外部 DTO 分离，并同步受影响的 DAO/Service 查询和持久化逻辑。
4. 面向已有安装设计迁移：处理已存在的字段、索引、约束和数据；保留租户及所有权；回填要有界且确定；评估 downgrade 或记录不可安全 downgrade 的原因。
5. 修改 MySQL 主键或外键时，检查全部依赖约束和索引。旧主键是外键唯一支持索引时，先创建显式支持索引，再删除主键，并检查离线 SQL 的操作顺序。
6. 新保护 Controller 的权限码要同步加入权限/菜单 seed。初始化 SQL 和 seed 必须幂等，不能包含真实凭据或生产数据。
7. 先做离线和测试验证：

```powershell
poetry run alembic upgrade head --sql
poetry run python -m pytest -q test/test_migration_config.py test/test_schema_integrity.py test/test_sql_init.py
```

8. 只有确认环境、目标、凭据来源和数据影响后，才执行 `scripts.migrate_database` 或 `fastapi-migrate` 写入真实 MySQL。不要用删除数据库卷排查普通迁移问题。
9. 迁移相关 API 测试、`git diff --check` 和 Compose 配置检查也要执行，并分别报告离线验证、本地测试和真实数据库执行结果。

## MySQL 安全规则

- 不直接修改生产表来让应用测试通过。
- 不假设 `DROP PRIMARY KEY` 与外键支持索引无关。
- 不依赖应用启动隐式修复任意 schema 漂移。
- 不把生成的 migration SQL、备份、dump 或真实数据提交到源码。

详细检查项见 [migration-checklist.md](references/migration-checklist.md)。
