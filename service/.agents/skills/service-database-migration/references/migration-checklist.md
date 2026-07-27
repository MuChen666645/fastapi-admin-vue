# 迁移检查表

## 设计

- [ ] 已检查当前迁移 head、DO、DAO、DTO、seed 和初始化 SQL。
- [ ] 已明确字段类型、可空性、默认值、索引、唯一约束、外键和租户/所有权字段。
- [ ] 已评估旧安装、已有数据、回填、重复执行和 downgrade。

## MySQL

- [ ] 主键、外键和支持索引的依赖关系已核对。
- [ ] 主键替换时支持索引先于 `DROP PRIMARY KEY`。
- [ ] 索引和 DDL 的重复执行行为已处理或明确限制。
- [ ] 没有使用删除数据卷或清空数据库绕过问题。

## 同步项

- [ ] DO、DTO、DAO、Service 和 Controller 行为同步。
- [ ] 新权限码、菜单和 seed 已更新。
- [ ] 初始化 SQL/历史升级 SQL 与迁移策略没有互相覆盖。

## 验证

- [ ] `poetry run alembic upgrade head --sql` 成功。
- [ ] 迁移、schema、SQL-init 和受影响 API 测试成功。
- [ ] 真实数据库执行是否完成已单独说明。
