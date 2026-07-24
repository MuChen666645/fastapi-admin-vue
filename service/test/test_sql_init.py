import re
from pathlib import Path

SQL_DIR = Path(__file__).parents[1] / "assets" / "sql"
SCHEMA_SQL_PATH = SQL_DIR / "schema-upgrade.sql"
SEED_SQL_PATH = SQL_DIR / "fastapi-admin.sql"


def test_department_upgrade_sql_is_idempotent() -> None:
    sql = SCHEMA_SQL_PATH.read_text(encoding="utf-8")

    assert "information_schema.COLUMNS" in sql
    assert "information_schema.STATISTICS" in sql
    assert "PREPARE add_dept_id_stmt" in sql
    assert "PREPARE add_dept_id_index_stmt" in sql


def test_organization_and_dictionary_seed_data_exists() -> None:
    sql = SEED_SQL_PATH.read_text(encoding="utf-8")

    assert "INSERT IGNORE INTO tenants" in sql
    assert "INSERT IGNORE INTO departments" in sql
    assert "INSERT IGNORE INTO posts" in sql
    assert "INSERT IGNORE INTO tenant_members" in sql
    assert "INSERT IGNORE INTO user_role (tenant_id, user_id, role_id)" in sql
    assert "INSERT IGNORE INTO user_post (tenant_id, user_id, post_id)" in sql
    assert "field:user:email" in sql
    assert "'sys_user_sex'" in sql
    assert "'sys_normal_disable'" in sql
    assert "'sys_yes_no'" in sql


def test_foreign_key_upgrade_sql_is_idempotent() -> None:
    sql = SCHEMA_SQL_PATH.read_text(encoding="utf-8")

    assert "information_schema.KEY_COLUMN_USAGE" in sql
    assert "DELETE ur" in sql
    assert "DELETE rm" in sql
    assert "DELETE up" in sql
    assert "ALTER TABLE departments MODIFY COLUMN parent_id INT NULL" in sql

    expected_constraints = {
        "fk_users_role",
        "fk_users_department",
        "fk_user_role_user",
        "fk_user_role_role",
        "fk_role_menu_role",
        "fk_role_menu_menu",
        "fk_user_post_user",
        "fk_user_post_post",
        "fk_departments_parent",
        "fk_menu_parent",
        "fk_login_logs_user",
        "fk_operation_logs_user",
        "fk_exception_logs_user",
    }
    assert all(name in sql for name in expected_constraints)


def test_sql_initialization_uses_utc8_and_null_root_departments() -> None:
    sql = SEED_SQL_PATH.read_text(encoding="utf-8")

    assert "SET time_zone = '+08:00'" in sql
    assert "SET @seed_tenant_id := 1" in sql
    assert "START TRANSACTION" in sql
    assert sql.rstrip().endswith("COMMIT;")
    assert sql.index("INSERT IGNORE INTO roles") < sql.index("INSERT IGNORE INTO users")
    assert "(@seed_tenant_id, 100, NULL, '0', '集团总部'" in sql


def test_tenant_scoped_seed_rows_include_the_default_tenant() -> None:
    sql = SEED_SQL_PATH.read_text(encoding="utf-8")

    for table_name in (
        "departments",
        "posts",
        "menu",
        "dict_types",
        "dict_data",
    ):
        match = re.search(
            rf"INSERT IGNORE INTO {table_name} \(\s*tenant_id\b", sql
        )
        assert match is not None, table_name

    users_block = sql[sql.index("INSERT IGNORE INTO users") : sql.index(
        "INSERT IGNORE INTO tenant_members"
    )]
    assert "tenant_id" in users_block
    assert "(1, CURRENT_TIMESTAMP, 'admin'" in users_block


def test_admin_menu_seed_is_scoped_to_declared_builtin_menu_ids() -> None:
    sql = SEED_SQL_PATH.read_text(encoding="utf-8")

    assert "SELECT r.id, m.menu_id" in sql
    assert "SET @seed_admin_role_code := 'admin'" in sql
    assert "WHERE r.code = @seed_admin_role_code" in sql
    assert "m.tenant_id = @seed_tenant_id" in sql
    assert "r.tenant_id = @seed_tenant_id" in sql
    assert "INSERT IGNORE INTO role_menu (role_id, menu_id)\nSELECT 1" not in sql


def test_seed_and_schema_upgrade_have_separate_responsibilities() -> None:
    seed_sql = SEED_SQL_PATH.read_text(encoding="utf-8").upper()
    schema_sql = SCHEMA_SQL_PATH.read_text(encoding="utf-8").upper()

    assert "CREATE TABLE" not in seed_sql
    assert "ALTER TABLE" not in seed_sql
    assert "INFORMATION_SCHEMA" not in seed_sql
    assert "INSERT IGNORE INTO" not in schema_sql


def test_seed_contains_every_controller_permission() -> None:
    controller_dir = Path(__file__).parents[1] / "module_admin" / "controller"
    controller_source = "\n".join(
        path.read_text(encoding="utf-8") for path in controller_dir.glob("*.py")
    )
    permission_codes = set(
        re.findall(
            r'(?:has_permission|permission)\("([^"]+)"\)',
            controller_source,
        )
    )
    seed_sql = SEED_SQL_PATH.read_text(encoding="utf-8")

    assert permission_codes
    assert all(f"'{code}'" in seed_sql for code in permission_codes)


def test_seed_is_idempotent_and_repairs_only_builtin_users() -> None:
    seed_sql = SEED_SQL_PATH.read_text(encoding="utf-8")

    assert seed_sql.count("INSERT IGNORE INTO") >= 10
    assert "UPDATE users AS u" in seed_sql
    assert "u.username IN ('admin', 'test')" in seed_sql
    assert "u.tenant_id IS NULL" in seed_sql
    assert "AND r.tenant_id = @seed_tenant_id" in seed_sql
    assert "AND p.tenant_id = @seed_tenant_id" in seed_sql
    assert "UPDATE tenant_members AS tm" in seed_sql
    assert "tm.deleted_at = NULL" in seed_sql
    assert seed_sql.index("INSERT IGNORE INTO tenant_members") < seed_sql.index(
        "UPDATE tenant_members AS tm"
    )
    assert seed_sql.index("UPDATE users AS u") < seed_sql.index(
        "INSERT IGNORE INTO tenant_members"
    )
    assert "UPDATE users SET" not in seed_sql
    assert "    id, name, code, module, permission_type" not in seed_sql
