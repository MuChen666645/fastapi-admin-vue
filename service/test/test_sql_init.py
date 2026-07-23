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

    assert "INSERT IGNORE INTO departments" in sql
    assert "INSERT IGNORE INTO posts" in sql
    assert "INSERT IGNORE INTO user_role (tenant_id, user_id, role_id)" in sql
    assert "INSERT IGNORE INTO user_post (tenant_id, user_id, post_id)" in sql
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
    assert sql.index("INSERT IGNORE INTO roles") < sql.index("INSERT IGNORE INTO users")
    assert "(100, NULL, '0', '集团总部'" in sql


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


def test_seed_is_idempotent_and_does_not_update_existing_users() -> None:
    seed_sql = SEED_SQL_PATH.read_text(encoding="utf-8")

    assert seed_sql.count("INSERT IGNORE INTO") >= 10
    assert "UPDATE users" not in seed_sql
