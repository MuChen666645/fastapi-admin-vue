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


def test_admin_operation_migration_is_present() -> None:
    migration = (
        ROOT / "alembic" / "versions" / "0003_admin_operations.py"
    ).read_text(encoding="utf-8")

    assert 'revision = "0003_admin_operations"' in migration
    for table_name in (
        '"file_metadata"',
        '"system_configs"',
        '"notices"',
        '"scheduled_jobs"',
        '"job_logs"',
    ):
        assert table_name in migration


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
    assert "MysqlServe.get_db_url()" in migration_source
    assert "MysqlServe.DB_URL" not in migration_source
    assert "service_completed_successfully" in compose
    assert "alembic_version" in health_source


def test_migration_entrypoint_expands_alembic_version_column() -> None:
    migration_source = (ROOT / "scripts" / "migrate_database.py").read_text(
        encoding="utf-8"
    )
    scheduler_migration = (
        ROOT / "alembic" / "versions" / "0009_scheduler_execution_controls.py"
    ).read_text(encoding="utf-8")

    assert "VARCHAR(64)" in migration_source
    assert '"timeout_seconds" not in columns' in scheduler_migration
    assert '"max_retries" not in columns' in scheduler_migration
    assert "context.is_offline_mode()" in scheduler_migration


def test_compose_and_deployment_profiles_use_matching_service_credentials() -> None:
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")

    assert "fastapi-mysql:" in compose
    assert "fastapi-redis:" in compose
    assert (
        "MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD:?MYSQL_ROOT_PASSWORD is required}"
        in compose
    )
    assert "MYSQL_USER: ${MYSQL_USERNAME:?MYSQL_USERNAME is required}" in compose
    assert "MYSQL_PASSWORD: ${MYSQL_PASSWORD:?MYSQL_PASSWORD is required}" in compose

    for filename in (".env.staging.example", ".env.production.example"):
        environment = (ROOT / filename).read_text(encoding="utf-8")
        assert "MYSQL_HOST=fastapi-mysql" in environment
        assert "REDIS_HOST=fastapi-redis" in environment
        assert "MYSQL_ROOT_PASSWORD=REPLACE_WITH_" in environment
