from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_alembic_has_an_initial_versioned_schema() -> None:
    config = (ROOT / "alembic.ini").read_text(encoding="utf-8")
    migration = (
        ROOT / "alembic" / "versions" / "0001_initial_schema.py"
    ).read_text(encoding="utf-8")

    assert "script_location = %(here)s/alembic" in config
    assert 'revision = "0001_initial_schema"' in migration
    assert "op.create_table" in migration
    assert "SQLModel.metadata" not in migration


def test_role_data_scope_migration_is_present() -> None:
    migration = (
        ROOT / "alembic" / "versions" / "0002_role_data_scope.py"
    ).read_text(encoding="utf-8")

    assert 'revision = "0002_role_data_scope"' in migration
    assert 'down_revision = "0001_initial_schema"' in migration
    assert '"role_dept"' in migration
    assert '"data_scope"' in migration


def test_application_startup_does_not_execute_legacy_sql_or_create_tables() -> None:
    main_source = (ROOT / "main.py").read_text(encoding="utf-8")
    mysql_source = (ROOT / "config" / "mysql_serve.py").read_text(encoding="utf-8")

    assert "assets/sql/" not in main_source
    assert "create_all" not in mysql_source


def test_migration_entrypoint_and_schema_readiness_are_configured() -> None:
    migration_source = (ROOT / "scripts" / "migrate_database.py").read_text(
        encoding="utf-8"
    )
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    health_source = (
        ROOT / "module_admin" / "controller" / "health_controller.py"
    ).read_text(encoding="utf-8")

    assert 'command.stamp(config, "0001_initial_schema")' in migration_source
    assert 'command.upgrade(config, "head")' in migration_source
    assert "service_completed_successfully" in compose
    assert "alembic_version" in health_source
