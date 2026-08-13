# FastAPI Admin Vue

> Enterprise multi-tenant administration platform built with a Vue 3 management console and a FastAPI service.

[中文](./README.md) | [Development Guide](./DEVELOPMENT.md) | [Repository Standards](./.codex/README.md)

## Overview

FastAPI Admin Vue is a decoupled enterprise administration platform. `frontend/` provides the Vue 3 management workspace.
`service/` provides versioned management APIs, authentication, authorization, tenant isolation, business rules, and data
persistence through FastAPI.

The project is designed for internal operations systems, multi-tenant back offices, and enterprise administration scenarios.

- **Server authority**: the backend enforces authentication, authorization, tenancy, data scope, business state, and consistency.
- **Contract driven**: the frontend calls verified `/api/v1` APIs through typed modules, parsers, and one request boundary.
- **Clear ownership**: frontend views, stores, APIs, and layouts are separated; backend controllers, services, DAOs, and the database are separated.
- **Verifiable delivery**: focused tests, static checks, builds, offline migration SQL, and required real-dependency checks validate changes in layers.

## Core Capabilities

| Domain                         | Capabilities                                                                                          |
| ------------------------------ | ----------------------------------------------------------------------------------------------------- |
| Identity and session           | Login, CAPTCHA, token refresh, password policy, forced password change, MFA, and session revocation   |
| Authorization and organization | Users, roles, menus, button permissions, field permissions, departments, posts, and data scopes       |
| Multi-tenancy                  | Tenant lifecycle, memberships, tenant switching, tenant isolation, and default-tenant protection      |
| System management              | Dictionaries, system parameters, message center, files, logs, and online sessions                     |
| Jobs and operations            | Cron jobs, execution logs, async exports, backups, health checks, metrics, and tracing                |
| Management experience          | Server routes, permission presentation, tabs, cache, theme, localization, timezone, and route loading |

Page and operation availability depends on server-provided menus, current user permissions, and deployed backend capabilities.

## Architecture

```text
Vue View / BasicLayout / Store
  -> Domain API and response Parser
  -> Unified request layer
  -> HTTP /api/v1
  -> FastAPI Controller
  -> Auth / Tenant / Data Scope
  -> Service business rules and transactions
  -> DAO / SQLModel
  -> MySQL / Redis / Worker / external services
```

Frontend menus, controls, and route guards improve usability only; they do not replace backend authorization. Server route
components can resolve only to the frontend's local view allowlist, and unknown component paths are never executed.

## Repository Layout

```text
.
├── frontend/                 # Vue 3 management console
│   ├── src/api/              # Domain APIs, request encoding, and response parsers
│   ├── src/layouts/          # BasicLayout, system-settings drawer, and application shell
│   ├── src/router/           # Static routes, guards, and dynamic-route conversion
│   ├── src/stores/           # Session, preferences, dictionary, tabs, message, and loading state
│   └── src/__tests__/        # Vitest behavior and contract tests
├── service/                  # FastAPI service
│   ├── module_admin/         # Controllers, services, DAOs, DOs, and DTOs
│   ├── alembic/              # Versioned database migrations
│   ├── assets/sql/           # Initialization and upgrade SQL
│   ├── scripts/              # Migration, backup, and worker entry points
│   └── test/                 # pytest contract, security, and regression tests
├── .agents/skills/           # Cross-project Agent Skills
├── .codex/                   # Repository engineering standards
└── DEVELOPMENT.md            # Development collaboration guide
```

## Quick Start

### Prerequisites

- Node.js: use the `engines` range in [frontend/package.json](./frontend/package.json).
- pnpm: frontend package manager.
- Python 3.11+ and Poetry: backend runtime and dependency management.
- MySQL 8.x and Redis 6.x+: runtime dependencies for the service.
- Docker Compose: required for containerized dependencies and deployment verification.

### 1. Start Backend Dependencies and Service

```powershell
Set-Location service
Copy-Item .env.development.example .env.development

docker compose --env-file .env.development up -d fastapi-mysql fastapi-redis
poetry install
$env:APP_ENV = "development"
$env:DEBUG = "true"
poetry run python -m scripts.migrate_database
poetry run uvicorn main:app --host 0.0.0.0 --port 3000 --reload
```

The service defaults to `http://127.0.0.1:3000`. Use `/api/v1/health/live` and `/api/v1/health/ready` for health checks.
In development, OpenAPI documentation is available at `/docs`.

### 2. Start Frontend

```powershell
Set-Location ..\frontend
Copy-Item .env.example .env.local
pnpm install
pnpm run dev
```

The frontend defaults to `http://127.0.0.1:5173`. The development proxy forwards `/api` to the service. `VITE_*` values are
included in browser output, so they must never contain passwords, tokens, secrets, or internal credentials.

### 3. Start the Complete Backend Stack with Docker Compose

```powershell
Set-Location service
docker compose --env-file .env.development up -d --build
```

This flow waits for MySQL and Redis health checks and a successful migration service before starting the application and worker.
Before production deployment, complete secret injection, Host/CORS hardening, TLS, backup, and readiness validation.

## Frontend-Service Contract

Management APIs use the backend `API_V1_PREFIX`, currently `/api/v1`. A standard successful JSON response follows:

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

Files, streams, and endpoints explicitly requiring raw responses do not use the JSON envelope. Current backend OpenAPI,
DTOs, controllers, and tests are authoritative for fields, pagination, status codes, permissions, and errors. Do not infer
them from this README.

When an API is added or changed, synchronize and verify:

1. Method, full path, Path/Query/Body/FormData, pagination, and sorting.
2. Success response, nullability, errors, files/streams, and response wrapping.
3. Authentication, permission codes, tenancy, data scope, ownership, idempotency, retries, and rollback.
4. Backend DTOs/controllers/services/DAOs/tests and frontend types/APIs/parsers/callers/tests.

## Development and Quality

Common verification commands:

```powershell
# Frontend
Set-Location frontend
pnpm run check
pnpm run test:run
pnpm run build

# Backend
Set-Location ..\service
$env:APP_ENV = "development"
$env:DEBUG = "true"
poetry run python -m pytest -q
poetry run python -m compileall -q main.py module_admin config middleware interceptors scripts alembic test
poetry run alembic upgrade head --sql

# Repository root
git diff --check
```

Run the closest relevant test first, then expand validation when changing the request layer, authentication, dynamic routing,
shared layout, migrations, builds, or runtime configuration. Unit tests, static checks, and offline SQL do not establish that
MySQL, Redis, Docker, browsers, OIDC/LDAP/SMTP, OSS, or production environments have been verified.

## Database and Background Jobs

Alembic manages the database schema. The current migration head is `0028_tenant_and_system_parameter_menus`. Applied files
under `service/alembic/versions/` are deployment history and must not be deleted, renamed, compacted, or rewritten; fixes use
new migrations.

Scheduled jobs run only when the backend scheduler is enabled and `task_name` matches a registered handler. A persisted job
record does not create its handler. Long-running work belongs in the scheduler, worker, or async export flow, not an HTTP request.

## Security and Release Boundaries

- Never commit real passwords, tokens, secrets, CAPTCHA or MFA values, production data, database backups, caches, coverage, or build output.
- The backend performs final authentication, authorization, tenant, data-scope, and ownership validation; hidden frontend controls are not security boundaries.
- Database migrations, backup/restore, Redis cleanup, Docker, external identity, OSS, SMTP, webhooks, and production actions require a confirmed environment, target, permission, and data impact.
- Do not commit, push, create pull requests, or operate remote resources unless explicitly requested.

## Documentation and Agent Skills

| Topic                                            | Entry Point                                                                                       |
| ------------------------------------------------ | ------------------------------------------------------------------------------------------------- |
| Repository development and integration standards | [DEVELOPMENT.md](./DEVELOPMENT.md), [.codex/README.md](./.codex/README.md)                        |
| Frontend documentation                           | [中文](./frontend/README.md) · [English](./frontend/README.en.md)                                 |
| Backend documentation                            | [中文](./service/README.md) · [English](./service/README.en.md)                                   |
| Cross-project contract changes                   | [.agents/skills/fullstack-contract-change](./.agents/skills/fullstack-contract-change/SKILL.md)   |
| Cross-project feature delivery                   | [.agents/skills/fullstack-feature-delivery](./.agents/skills/fullstack-feature-delivery/SKILL.md) |
| Integration validation                           | [.agents/skills/fullstack-validation](./.agents/skills/fullstack-validation/SKILL.md)             |
| Repository review                                | [.agents/skills/repository-code-review](./.agents/skills/repository-code-review/SKILL.md)         |

## License

This repository does not currently declare a license. Add an appropriate license, third-party dependency compliance statement,
and release policy before external distribution or commercial delivery.
