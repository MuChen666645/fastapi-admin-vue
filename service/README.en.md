# FastAPI Admin Vue Service

> [中文](./README.md) | English

FastAPI Admin Vue Service is the backend service for FastAPI Admin Vue. It provides enterprise administration capabilities for identity, RBAC, tenant isolation, organization data, system parameters, messages, files, scheduled jobs, and operational observability.

The service collaborates with `frontend/` through HTTP contracts. Authentication, authorization, tenancy, data scope, business state, and data consistency are enforced by the backend.

## Scope

| Domain | Capability | API prefix |
| --- | --- | --- |
| Identity | Login, token refresh, captcha, MFA, password policy, recovery | `/api/v1/user`, `/api/v1/captcha` |
| RBAC | Users, roles, menus, button permissions, field permissions, data scopes | `/api/v1/user`, `/api/v1/role`, `/api/v1/menu` |
| Organization | Departments, posts, dictionary types and data | `/api/v1/dept`, `/api/v1/post`, `/api/v1/dict` |
| Multi-tenancy | Tenant lifecycle, memberships, tenant switching | `/api/v1/tenant` |
| System | System parameters, messages, logs, online sessions | `/api/v1/config`, `/api/v1/message`, `/api/v1/log`, `/api/v1/online` |
| Files and jobs | Files, exports, scheduled jobs, backups, health, metrics | `/api/v1/file`, `/api/v1/job`, `/api/v1/ops/backup`, `/api/v1/health`, `/metrics` |
| External identity | OIDC/OAuth and LDAP login | `/api/v1/auth` |

The seed data exposes **System Parameters** and **Tenant Management** under System Management. Their components are `system/config/index` and `system/tenant/index`. The frontend must provide these views and integrate the verified APIs before exposing the pages.

## Architecture

```text
HTTP Client -> FastAPI -> /api/v1 Controller -> Service -> DAO -> MySQL
                                      |             |
                                      +-- Auth/Redis +-- Tenant and data-scope filters
```

Controllers adapt HTTP requests and dependencies. Services own business rules and transaction orchestration. DAOs only access data. HTTP requests use `request.state.mysql`; scheduler, audit, export, and worker flows use `app.state.mysql_session_factory`.

Key directories are `module_admin/controller` (routes), `module_admin/service` (business logic), `module_admin/dao` (persistence), `module_admin/entity/do` (SQLModel tables), `module_admin/entity/dto` (Pydantic contracts), `alembic` (migrations), `assets/sql` (seed SQL), `scripts` (operations), and `test` (tests).

## API and Response Contract

- Management APIs use `API_V1_PREFIX`, defaulting to `/api/v1`; unversioned compatibility routes are not provided.
- Controllers declare module prefixes such as `/tenant` and `/config`; `module_admin/v1.py` applies the global prefix.
- Standard JSON responses are `{ "code": 200, "message": "success", "data": ... }`. Errors use the shared error structure and include `error_code`; files and streams keep native responses.
- `/docs`, `/redoc`, and `/openapi.json` are the API-contract sources and require `DOCS_AUTH_TOKEN` outside development.
- `/api/v1/health/live` reports process liveness. `/api/v1/health/ready` checks MySQL, Redis, and migration readiness.

Use the current OpenAPI and DTOs for fields, status codes, permissions, and pagination. Do not infer contracts from an older README.

## Authentication, Authorization, and Tenancy

Protected endpoints use:

```http
Authorization: Bearer <access_token>
```

The service validates JWT signatures, expiry, cache state, user state, password version, and revocation. Access and refresh tokens rotate; reuse of a rotated refresh token revokes its token family. Captcha, failed-login locking, password policy, forced password change, and MFA are handled centrally.

- Routes use `Depends(Auth.has_permission("system:resource:action"))` for button-level authorization.
- `permissions` is the permission catalog. Button menus (`menu_type = F`) map `perms` to codes, and `role_menu` stores grants.
- `*:*:*` is the platform super-administrator wildcard; platform tenant operations also require `Auth.platform_admin_status`.
- Field permissions use `field:<resource>:<field>`. Data scopes include all data, department, descendants, custom departments, and self.
- Reads and writes validate the active tenant, data scope, and resource ownership. Hidden frontend controls are not an authorization boundary.

## Environment and Configuration

Requirements: Python 3.11+, Poetry 1.8+, MySQL 8.x, Redis 6.x+, and Docker Compose for containers.

`APP_ENV` selects `.env.development`, `.env.staging`, or `.env.production`; process variables take precedence. `APP_ENV_FILE` only selects a Compose `env_file`.

```powershell
Copy-Item .env.development.example .env.development
$env:APP_ENV = "development"
$env:DEBUG = "true"
```

Primary settings are `API_V1_PREFIX`, `MYSQL_*`, `REDIS_*`, `SECRET_KEY`, `ADMIN_ROLE_CODE`, `PASSWORD_*`, `MFA_*`, `RATE_LIMIT_*`, `SCHEDULER_*`, `FILE_*`, `OSS_*`, `OTEL_*`, `DOCS_AUTH_TOKEN`, and `METRICS_AUTH_TOKEN`. Never commit real credentials or production endpoints. Staging and production must disable Debug and restrict Host/CORS.

## Local Development

```bash
poetry install
docker compose --env-file .env.development up -d fastapi-mysql fastapi-redis
poetry run python -m scripts.migrate_database
poetry run uvicorn main:app --host 0.0.0.0 --port 3000 --reload
```

Service: `http://127.0.0.1:3000`; OpenAPI: `/docs`; ReDoc: `/redoc`; readiness: `/api/v1/health/ready`.

## Database Migrations and Seed Data

Schema changes are managed exclusively through Alembic:

```bash
poetry run python -m scripts.migrate_database
poetry run alembic upgrade head --sql > migration.sql
```

`assets/sql/fastapi-admin.sql` is an explicitly executed, repeatable deployment seed. It creates the default tenant, built-in users, roles, organization data, menus, permission catalog, role-menu assignments, and dictionaries. It uses fixed IDs, a transaction, and `INSERT IGNORE`; application startup never executes it.

```bash
mysql --host 127.0.0.1 --port 3306 --user YOUR_MYSQL_USER --password=YOUR_MYSQL_PASSWORD --database fastapi_admin < assets/sql/fastapi-admin.sql
```

Migration `0028_tenant_and_system_parameter_menus` adds Tenant Management and eight tenant-operation buttons for the default tenant, standardizes menu `351` as System Parameters, and grants the new built-in menus to the administrator role.

## Container Deployment

The migration service must complete before the FastAPI application starts:

```bash
docker compose --env-file .env.development up -d --build
docker compose --env-file .env.staging up -d --build
docker compose --env-file .env.production --profile production up -d --build
```

Before production rollout, complete secret injection, backup, TLS, Host/CORS restriction, and readiness validation.

```bash
docker compose --env-file .env.development logs -f fastapi-migrate
docker compose --env-file .env.development logs -f fastapi-app
docker compose --env-file .env.development config
```

## Scheduling and Background Tasks

- APScheduler is created only when `SCHEDULER_ENABLED=true`.
- Each `/api/v1/job` `task_name` must exactly match a handler registered with `create_app(job_tasks={...})`; a database row does not create a handler.
- `SCHEDULER_WORKER_MODE=inline` runs handlers in the web process. `queue` uses Redis Streams and `scripts.task_worker`.
- Redis distributed locks prevent duplicate multi-instance execution. Jobs support timeout, retry, pause/resume, and execution logs.
- Long-running work belongs in the scheduler, worker, or async export flow, not in an HTTP request thread.

```python
from main import create_app

app = create_app(job_tasks={"example.task": lambda args: "ok"})
```

## Observability and Security

- Requests return `X-Request-ID`, `X-Trace-ID`, `X-Span-ID`, and `traceparent`.
- `/metrics` exposes HTTP, dependency, job, and notification metrics; outside development it requires `METRICS_AUTH_TOKEN`.
- Set `OTEL_ENABLED=true` to export traces to `OTEL_EXPORTER_OTLP_ENDPOINT`; failed jobs can alert through `ALERT_WEBHOOK_URL`.
- Mutations retain idempotency, authentication, authorization, tenant, data-scope, and ownership checks; batch operations record audit snapshots.
- File uploads validate extension, size, and content signature. Sensitive system parameters are encrypted and masked in API output.
- Backup and restore are controlled operations. Online restore is disabled by default and requires maintenance, an operations token, and MFA.

## Quality Validation

```powershell
$env:APP_ENV = "development"
$env:DEBUG = "true"

poetry run python -m compileall -q main.py module_admin config middleware interceptors scripts alembic test
poetry run python -m pytest -q -m "not integration"
poetry run black --check path/to/changed_file.py
poetry run isort --check-only --profile black .
poetry run flake8 --max-line-length=88 .
```

Real MySQL/Redis integration validation:

```bash
docker compose --env-file .env.development up -d fastapi-mysql fastapi-redis
poetry run python -m scripts.migrate_database
RUN_INTEGRATION_TESTS=1 poetry run python -m pytest -q -m integration
```

Report integration, OSS, SMTP, OIDC/LDAP, and production-deployment results separately from local unit-test results.

## Troubleshooting

**Missing environment variables:** verify the file selected by `APP_ENV` exists and required MySQL, Redis, and `SECRET_KEY` values are available. `APP_ENV_FILE` does not replace `APP_ENV` for a directly started Uvicorn process.

**Scheduler disabled or handler not registered:** set `SCHEDULER_ENABLED=true`, restart, and verify that `task_name` exactly matches a key in `create_app(job_tasks={...})`.

**Menu exists but its page is unavailable:** verify role menu/button permissions and the frontend view targeted by `component`; backend menu data does not generate frontend pages.

**Readiness probe fails:** check MySQL, Redis, and `alembic_version`; liveness does not establish dependency readiness.

## License

This repository does not currently declare a license. Add an appropriate license and third-party compliance statement before external distribution or commercial delivery.
