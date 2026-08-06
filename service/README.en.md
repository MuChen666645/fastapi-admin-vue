# FastAPI Admin Vue Service

> [中文](./README.md) | English

FastAPI Admin Vue Service is a backend service for an admin management system built with **FastAPI, SQLModel, MySQL, and Redis**. It follows a layered architecture and includes user management, role management, menu management, captcha, JWT authentication, button-level authorization, response interception, request logging, rate limiting, static files, and Docker deployment support.

## Features

- Async FastAPI Web API service
- SQLModel + SQLAlchemy AsyncSession data access
- MySQL persistence
- Redis cache, captcha storage, token cache, and cross-process shared rate limiting
- JWT login authentication, memory/Redis token validation, and button-level route authorization
- Rotating access/refresh tokens, disabled-user rejection, password policy, forced password change, MFA, and password recovery
- User, role, and menu management modules with menu button permission synchronization
- RuoYi-style RBAC model with super-admin wildcard permission `*:*:*`
- Tenant isolation, field-level permissions, data scopes, and permission-change auditing
- Image captcha generation/verification; the plaintext numeric endpoint is disabled
- Unified response interception and exception handling with sanitized 500 responses
- Request IDs, W3C `traceparent` correlation, and structured JSON logs
- File signature checks, optional ClamAV scanning, chunked uploads, presigned URLs, and text redaction
- Excel import/export for users, roles, and dictionaries, message delivery, and encrypted database backups
- Tenant memberships, tenant switching, soft deletion, optimistic locking, strict tenant-scoped queries, and rollback-safe writes
- Idempotency keys for mutating requests and before/after audit snapshots for batch operations
- Redis Streams task queue with an independent Worker, worker heartbeats, lock renewal, timeout, and retry controls
- Versioned Secret Manager encryption, masked sensitive config, key rotation, encrypted backup verification, and restore rehearsal tooling
- Inbox, webhook, email, and SMS notification delivery with bounded exponential retries
- Redis-distributed job locks, timeout/retry/pause controls, Prometheus metrics, and optional OTLP traces
- Local/Aliyun OSS file upload and download, system config, message center, and scheduled jobs
- Prometheus metrics available at `/metrics` (protected by `METRICS_AUTH_TOKEN` outside development)
- SlowAPI rate limiting
- All admin routes use the versioned `/api/v1` prefix.
- Swagger/OpenAPI API documentation with concrete per-route response DTOs; operations endpoints require `DOCS_AUTH_TOKEN` outside development
- Dockerfile and Docker Compose setup
- Poetry dependency management
- pre-commit, Black, isort, flake8, and Commitizen workflow

## Tech Stack


| Category              | Technology             |
| --------------------- | ---------------------- |
| Web Framework         | FastAPI                |
| ASGI Server           | Uvicorn                |
| Data Models           | Pydantic, SQLModel     |
| Database              | MySQL                  |
| Database Driver       | aiomysql               |
| Cache                 | Redis                  |
| Authentication        | PyJWT                  |
| Password Hashing      | passlib                |
| Pagination            | fastapi-pagination     |
| Rate Limiting         | slowapi                |
| Logging               | loguru                 |
| Image Processing      | Pillow                 |
| Dependency Management | Poetry                 |
| Containerization      | Docker, Docker Compose |

## Project Structure

```text
.
|-- assets/                 # SQL seed scripts, fonts, and other assets
|   |-- font/
|   `-- sql/
|-- config/                 # Environment, MySQL, and Redis configuration
|-- interceptors/           # Exception interceptors
|-- middleware/             # Logging and response middleware
|-- module_admin/           # Admin business module
|   |-- auth/               # JWT and authorization logic
|   |-- controller/         # API route layer
|   |-- dao/                # Data access layer
|   |-- entity/
|   |   |-- do/             # SQLModel table models
|   |   `-- dto/            # Pydantic request/response models
|   `-- service/            # Business logic layer
|-- static/                 # Static files
|-- alembic/                # Versioned database migrations
|-- scripts/                # Deployment and migration entrypoints
|-- test/                   # Test directory
|-- utils/                  # Shared utilities
|-- main.py                 # FastAPI application entry
|-- pyproject.toml          # Poetry and tooling configuration
|-- Dockerfile
`-- docker-compose.yml
```

## Architecture

The project follows this layered flow:

```text
Controller -> Service -> DAO -> Database
```

- `controller`: defines routes, receives parameters, and wires dependencies.
- `service`: contains business logic, orchestration, and permission-related rules.
- `dao`: handles database queries and persistence.
- `entity/dto`: defines API request and response schemas.
- `entity/do`: defines database table models.

### Runtime Flow

```text
Request
  -> correlation and observability middleware
  -> logging, rate limiting, and response middleware
  -> request-scoped MySQL session dependency
  -> Controller -> Service -> DAO
  -> MySQL / Redis / file storage
```

- `main.create_app()` assembles middleware, exception handlers, static files, pagination, and admin routes.
- Startup creates Redis and MySQL clients and optionally starts the scheduler. Alembic migrations are applied by `scripts.migrate_database`, not by application startup DDL.
- `/api/v1/health/live` only reports process liveness. `/api/v1/health/ready` checks Redis, MySQL, and `alembic_version` before returning success.
- Business requests use the request-scoped transaction in `request.state.mysql`; audit logs use an independent session so rollback does not hide the failure record.

### Documentation and Comment Rules

- Production modules, classes, functional methods, and important helpers use Chinese docstrings that explain responsibility, inputs/outputs, transaction boundaries, and security constraints.
- Configuration constants, permission constants, cache-key prefixes, regular expressions, and runtime state use adjacent comments explaining their purpose.
- Pydantic/SQLModel fields use `title` or `description`; routes use `summary`. The generated OpenAPI document is the source of truth for full schemas.
- Comments explain why and cross-module constraints rather than restating obvious code. Update docstrings and README when behavior changes.
- New business logic follows `Controller -> Service -> DAO` boundaries and documents side effects involving permissions, data scope, cache consistency, and resource cleanup.

## Requirements

- Python 3.11+
- Poetry 1.8+
- MySQL 8.x
- Redis 6.x+
- Docker / Docker Compose, optional

## Environment Variables

The service selects one profile with `APP_ENV`: `development`, `staging`, or `production`. Development loads `.env.development`; shared environments load `.env.staging` or `.env.production`, which should be created locally from the matching example file. Environment variables exported by the process always take precedence over files.

```env
# Profile selection
APP_ENV=development
APP_ENV_FILE=.env.development

# FastAPI
DEBUG=true
TITLE=FastAPI Admin
SUMMARY=FastAPI, SQLModel, MySQL and Redis admin service.
VERSION=0.0.1
OPENAPI_URL=/openapi.json

# MySQL
MYSQL_HOST=127.0.0.1
MYSQL_POST=3306
MYSQL_USERNAME=fastapi_app
MYSQL_PASSWORD=your_mysql_password
MYSQL_ROOT_PASSWORD=your_mysql_root_password
MYSQL_DATABASES=fastapi_admin
TIMEZONE=Asia/Shanghai

# Redis
REDIS_HOST=127.0.0.1
REDIS_USERNAME=
REDIS_PASSWORD=your_redis_password
REDIS_POST=6379
REDIS_DB=0

# Aliyun OSS
ACCESS_KEY_ID=your_access_key_id
ACCESSKEY_SECRET=your_access_key_secret
OSS_ENDPOINT=
OSS_BUCKET=
OSS_PREFIX=uploads

# File storage
FILE_STORAGE_BACKEND=local
FILE_UPLOAD_DIR=uploads
FILE_MAX_SIZE_BYTES=10485760
FILE_PRESIGN_TTL_SECONDS=300
FILE_CONTENT_SNIFF_ENABLED=true
FILE_VIRUS_SCAN_ENABLED=false
FILE_REDACTION_ENABLED=false
FILE_CHUNK_TTL_SECONDS=86400
CLAMAV_HOST=clamav
CLAMAV_PORT=3310
FILE_ALLOWED_EXTENSIONS=[".jpg",".jpeg",".png",".gif",".webp",".pdf",".doc",".docx",".xls",".xlsx",".zip"]

# Scheduler
SCHEDULER_ENABLED=false
SCHEDULER_TIMEZONE=Asia/Shanghai
SCHEDULER_DEFAULT_TIMEOUT_SECONDS=300
SCHEDULER_LOCK_TTL_SECONDS=900
SCHEDULER_DEFAULT_MAX_RETRIES=0

# Observability, backup, and optional identity providers
OTEL_ENABLED=false
OTEL_SERVICE_NAME=fastapi-admin
OTEL_EXPORTER_OTLP_ENDPOINT=
OTEL_EXPORTER_OTLP_HEADERS=
LOG_RETENTION_DAYS=30
ALERT_WEBHOOK_URL=
BACKUP_DIR=backups
BACKUP_ENCRYPTION_KEY=
BACKUP_REHEARSAL_DATABASE=fastapi_admin_restore_rehearsal
BACKUP_ONLINE_RESTORE_ENABLED=false
BACKUP_RESTORE_MAINTENANCE_MODE=false
BACKUP_RESTORE_OPERATIONS_TOKEN=
BACKUP_RETENTION_DAYS=30
BACKUP_TIMEOUT_SECONDS=900
IDEMPOTENCY_RETENTION_DAYS=2
BATCH_AUDIT_RETENTION_DAYS=90
NOTIFICATION_RETENTION_DAYS=30
RETENTION_CLEANUP_INTERVAL_SECONDS=3600
OIDC_ENABLED=false
OIDC_AUTHORIZATION_URL=
OIDC_TOKEN_URL=
OIDC_USERINFO_URL=
OIDC_CLIENT_ID=
OIDC_CLIENT_SECRET=
OIDC_REDIRECT_URI=
OIDC_SCOPES=openid profile email
OIDC_ISSUER=
OIDC_AUDIENCE=
OIDC_JWKS_URL=
LDAP_ENABLED=false
LDAP_SERVER_URL=
LDAP_BASE_DN=
LDAP_BIND_DN=
LDAP_BIND_PASSWORD=
LDAP_USER_FILTER=(uid={username})

# Security and optional settings
SECRET_KEY=generate_a_random_secret_at_least_32_characters_long
ACCESS_TOKEN_EXPIRE_MINUTES=3600
ADMIN_ROLE_CODE=admin
RATE_LIMIT_DEFAULT=300/minute
RATE_LIMIT_LOGIN=10/minute
RATE_LIMIT_CAPTCHA=30/minute
RATE_LIMIT_REFRESH_TOKEN=30/minute
RATE_LIMIT_PASSWORD_RESET=5/minute
RATE_LIMIT_EXTERNAL_AUTH=10/minute
CAPTCHA_TTL_SECONDS=300
CAPTCHA_MAX_VERIFY_ATTEMPTS=5
LOGIN_MAX_FAILED_ATTEMPTS=5
LOGIN_IP_LOCK_SECONDS=300
LOGIN_ACCOUNT_MAX_FAILED_ATTEMPTS=5
LOGIN_ACCOUNT_LOCK_SECONDS=900
PASSWORD_MIN_LENGTH=12
PASSWORD_REQUIRE_UPPERCASE=true
PASSWORD_REQUIRE_LOWERCASE=true
PASSWORD_REQUIRE_DIGIT=true
PASSWORD_REQUIRE_SPECIAL=true
PASSWORD_HISTORY_COUNT=5
PASSWORD_MAX_AGE_DAYS=90
PASSWORD_FORCE_CHANGE_ON_CREATE=true
REFRESH_TOKEN_EXPIRE_DAYS=30
MFA_ISSUER=FastAPI Admin
PASSWORD_RESET_TOKEN_TTL_SECONDS=900
PASSWORD_RESET_EMAIL_ENABLED=false
PASSWORD_RESET_SMS_WEBHOOK=
SMTP_HOST=
SMTP_PORT=465
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_FROM=
READINESS_TIMEOUT_SECONDS=5
HOSTS=["localhost","127.0.0.1"]
TRUSTED_PROXIES=[]
ORIGINS=["http://localhost:5173"]
MEDOTHS=["GET","POST","PUT","DELETE","OPTIONS"]
HEADERS=["*"]
CREDENTIALS=false
```

> Note: `MYSQL_POST`, `REDIS_POST`, `MEDOTHS`, and `ACCESSKEY_SECRET` are the actual setting names used by the current codebase. Keep them unchanged unless the code is updated.

> Compose uses `fastapi-mysql` and `fastapi-redis` as fixed service names. `MYSQL_PASSWORD` belongs to the application account `MYSQL_USERNAME`; `MYSQL_ROOT_PASSWORD` is reserved for MySQL root health checks and administration. Compose creates the application account on first initialization.

> Except for code invariants such as `DATABASE_SCHEMA_VERSION`, deployment settings have no code-level defaults. Copy the matching `.example` file and fill every value. A `SECRET_KEY` change invalidates previously issued JWTs.

## Environment Profiles

| Profile | Configuration | Production checks |
| --- | --- | --- |
| Development | `.env.development` | Allows local-only defaults and debug logging |
| Staging | `.env.staging` from `.env.staging.example` | Requires generated secrets, `DEBUG=false`, and restricted hosts/origins |
| Production | `.env.production` from `.env.production.example` | Requires generated secrets, `DEBUG=false`, and restricted hosts/origins |

For staging or production, copy the example file, replace every `REPLACE_WITH_...` value, then start with the matching `APP_ENV`. The service also supports secret-store injection through process environment variables, so the real environment file does not need to be copied into the image or container. Do not commit it.

## Local Development

### 1. Install dependencies

```bash
poetry install
```

### 2. Select the local environment

The application reads `.env.<APP_ENV>` according to `APP_ENV`. `APP_ENV_FILE` is used by Docker Compose to select the container `env_file`; it does not select the file for a direct `uvicorn` process. Copy the matching example and fill in its values before starting:

```powershell
Copy-Item .env.development.example .env.development
Copy-Item .env.staging.example .env.staging
Copy-Item .env.production.example .env.production
```

When running directly on the host, change `MYSQL_HOST=fastapi-mysql` and `REDIS_HOST=fastapi-redis` in staging/production configurations to reachable host addresses such as `127.0.0.1`; those service names are available only inside the Compose network.

PowerShell commands:

```powershell
# development
$env:APP_ENV = "development"
poetry run uvicorn main:app --host 0.0.0.0 --port 3000 --reload

# staging
$env:APP_ENV = "staging"
poetry run uvicorn main:app --host 0.0.0.0 --port 3000

# production
$env:APP_ENV = "production"
poetry run uvicorn main:app --host 0.0.0.0 --port 3000
```

Bash/Linux commands:

```bash
APP_ENV=development poetry run uvicorn main:app --host 0.0.0.0 --port 3000 --reload
APP_ENV=staging poetry run uvicorn main:app --host 0.0.0.0 --port 3000
APP_ENV=production poetry run uvicorn main:app --host 0.0.0.0 --port 3000
```

### 3. Prepare MySQL and Redis

You can use local services or start only the dependency services with Docker Compose:

```bash
docker compose --env-file .env.development up -d fastapi-mysql fastapi-redis
```

### 4. Create the database

If you are not using the default database from `docker-compose.yml`, create it manually:

```sql
CREATE DATABASE fastapi_admin DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Database schema changes are managed by the migration service before the application starts. Existing installations without `alembic_version` are detected, stamped at `0001_initial_schema`, and upgraded to the current head. A persistent database volume does not rotate its MySQL password when an environment file changes; rotate the credential explicitly or use a new volume only after taking a backup.

The database uses UTC+8 consistently: Docker Compose passes MySQL `--default-time-zone=+08:00`, while application connections and SQL initialization scripts explicitly set the session time zone as well. API date-time values use `YYYY-MM-DD HH:mm:ss`. After restarting an existing database, verify `SELECT @@global.time_zone, @@session.time_zone;` and confirm both values match the deployment requirement.

### 5. Migrate and seed data

`APP_ENV` determines which database configuration the migration uses. Run the migration and then load the seed data explicitly:

```bash
poetry run python -m scripts.migrate_database
mysql --host 127.0.0.1 --port 3306 --user YOUR_MYSQL_USER --password=YOUR_MYSQL_PASSWORD --database fastapi_admin < assets/sql/fastapi-admin.sql
```

After startup, open:

- API service: `http://127.0.0.1:3000`
- Swagger docs: `http://127.0.0.1:3000/docs`
- ReDoc docs: `http://127.0.0.1:3000/redoc`
- OpenAPI JSON: `http://127.0.0.1:3000/openapi.json`

## Docker Deployment

### 1. Select the Docker environment

Copy and fill the matching environment file first. `--env-file` supplies Compose interpolation variables, while `APP_ENV_FILE` makes the application, migration, MySQL, and Redis containers load the same profile.

Development:

```bash
docker compose --env-file .env.development up -d --build
```

Staging:

```bash
docker compose --env-file .env.staging up -d --build
```

Production: prepare `certs/fullchain.pem` and `certs/privkey.pem`, then enable the `fastapi-edge` profile:

```bash
docker compose --env-file .env.production --profile production up -d --build
```

After the first deployment, load seed data after the migration service completes:

```bash
docker compose --env-file .env.development exec -T fastapi-mysql sh -c 'mysql -uroot -p"$MYSQL_ROOT_PASSWORD" fastapi_admin' < assets/sql/fastapi-admin.sql
```

Replace `.env.development` with the selected staging or production file. Do not use development settings or `--watch` in production.

### 2. View logs

```bash
docker compose logs -f fastapi-app
```

### 3. Stop services

```bash
docker compose down
```

Default port mapping:


| Service | Container Port | Host Port |
| ------- | -------------- | --------- |
| FastAPI | 3000           | 127.0.0.1:3000 |
| MySQL   | 3306           | 127.0.0.1:3306 |
| Redis   | 6379           | 127.0.0.1:6379 |
| Nginx (production profile) | 80/443 | 80/443 |

The base Compose profile binds FastAPI, MySQL, and Redis to localhost. The production profile exposes only Nginx on ports 80/443 and proxies HTTPS traffic to FastAPI. Before staging or production deployment, copy the matching `.env.*.example`, replace every placeholder, prepare TLS certificates, and start Compose with `--env-file` pointing to the resulting file.

## API Modules


| Module       | Route Prefix | Description                                                         |
| ------------ | ------------ | ------------------------------------------------------------------- |
| User         | `/api/v1/user`      | User creation, login, self-service password change, administrator password reset, user info |
| Role         | `/api/v1/role`      | Role creation, list, detail, update, delete                         |
| Menu         | `/api/v1/menu`      | Menu creation, tree/list query, detail, update, delete               |
| Department   | `/api/v1/dept`      | Department tree query, create, update, delete                        |
| Post         | `/api/v1/post`      | Post list, create, update, delete                                     |
| Dictionary   | `/api/v1/dict`      | Dictionary type and dictionary data CRUD                              |
| Logs         | `/api/v1/log`       | Login, operation, exception log query and deletion                    |
| Online Users | `/api/v1/online`    | Online session query and forced logout                                |
| Captcha      | `/api/v1/captcha`   | Image captcha/verification; the plaintext numeric endpoint returns `410` |
| Health       | `/api/v1/health`    | Liveness and MySQL/Redis readiness probes                         |
| Metrics      | `/metrics`   | Prometheus request count, status, and latency metrics              |
| File Storage | `/api/v1/file`      | Local or Aliyun OSS upload, download, and deletion                 |
| System Config| `/api/v1/config`    | Key/value system parameters                                        |
| Message Center| `/api/v1/message`   | Message management, personal messages, unread count, and read state |
| Jobs         | `/api/v1/job`       | Cron job management, manual run, and execution logs               |
| External Auth| `/api/v1/auth`      | OIDC/OAuth and LDAP login                                          |
| Backups      | `/api/v1/ops/backup`| Permission-protected database backup operations                    |
| Static Files | `/static`    | Static file access                                                  |

Use Swagger docs as the source of truth for full request and response schemas.

`GET /api/v1/captcha/image` returns a `captcha_id` and a Base64 image. Username login, phone login, and `GET /api/v1/captcha/verify` must submit both the `captcha_id` and the code shown in the image. The ID is bound to the client IP and is consumed after a successful verification. It is also deleted after `CAPTCHA_MAX_VERIFY_ATTEMPTS` failures, and expires after `CAPTCHA_TTL_SECONDS`.

## Authentication

Login APIs return a JWT token. For protected APIs, send it in the request header:

```http
Authorization: Bearer <access_token>
```

The token is signed with the `HS256` algorithm. Expiration is controlled by `ACCESS_TOKEN_EXPIRE_MINUTES`. After successful login, the token is cached in both process memory and Redis. The Redis key format is `auth:token:{sha256(token)}`.

Protected APIs check the in-memory cache first and then Redis. If both caches miss, the API returns `401 Token Not Found`. After a cache hit, the service still validates the JWT signature, expiration, and user status. The Redis TTL follows the token expiration time.

## Permissions and Response Models

- Routes use `Depends(Auth.has_permission("permission:code"))` for button-level authorization, for example `system:menu:edit`.
- The `permissions` table is the permission catalog. Button menus with `menu_type = F` connect `menu.perms` to `permissions.code`.
- Creating or updating a button menu syncs the permission catalog. Deleting a button menu removes the permission only when the same code is not used by other button menus.
- Roles connect to menus and button permissions through `role_menu`; authorization checks the user's roles, menu buttons, and permission catalog together.
- The super-admin wildcard `*:*:*` is stored in `permissions`, not returned as a menu. Users with the wildcard permission only need `*:*:*` in the returned permission list.
- `PUT /api/v1/user/{user_id}/password` is the self-service change-password endpoint and requires the old password. `PUT /api/v1/user/{user_id}/reset-password` is the administrator reset endpoint, uses `system:user:resetPwd`, and revokes the target user's active sessions after success.
- Login checks user status before issuing a token. A disabled user receives `用户已停用` and never receives a usable token.
- Validation failures keep structured `422` details under `data.errors`; clients should not parse a stringified exception.
- MySQL URLs are assembled with SQLAlchemy `URL.create()`, so usernames and passwords containing `@`, `:`, or `/` do not need manual escaping.
- Data scope is role-based and uses the union of all enabled roles assigned to the actor. Scope values are `1` all data, `2` selected departments, `3` current department, `4` current department and descendants, and `5` self only.
- `role_dept` stores selected departments for scope `2`. The service applies scope predicates to user, department, post, log, and online-session queries, and checks the same scope before detail, mutation, deletion, and forced logout operations.
- Role and menu configuration remains global system configuration. Changing a role's menus or data scope is restricted to super administrators; non-admin writes cannot use data scope as an escalation path.
- Runtime API responses are wrapped as `{ "code": 200, "message": "success", "data": ... }`. Unexpected failures return a sanitized 500 response while full tracebacks remain in server logs. Swagger uses `ApiResponseDto[T]` per route so response bodies show concrete schemas instead of `Any`.

## Common Commands

```bash
# Install dependencies
poetry install

# Apply schema migrations
poetry run python -m scripts.migrate_database

# Start development server
poetry run uvicorn main:app --host 0.0.0.0 --port 3000 --reload

# Run tests
poetry run python -m pytest -q

# Run unit tests and enforce the 60% coverage threshold
poetry run python -m pytest -q -m "not integration" --cov --cov-report=term-missing

# Start the local real MySQL/Redis services. Tests use randomized temporary rows
# and clean them up after each test.
docker compose up -d fastapi-mysql fastapi-redis
poetry run python -m scripts.migrate_database

# Run MySQL/Redis integration tests
RUN_INTEGRATION_TESTS=1 poetry run python -m pytest -q -m integration

# Run the real admin API tests without mocked services
RUN_INTEGRATION_TESTS=1 poetry run python -m pytest -q test/test_admin_api_async.py

# Verify an online migration downgrade followed by a fresh upgrade
poetry run alembic downgrade base
poetry run python -m scripts.migrate_database

# Verify encrypted backup, backup structure, and isolated restore rehearsal
poetry run python -m scripts.backup_database backup
poetry run python -m scripts.backup_database verify <filename>
poetry run python -m scripts.backup_database rehearse <filename>

# Create an isolated application for tests or multiple instances
from main import create_app
application = create_app()

# Register scheduled task handlers explicitly; task_name in /api/v1/job must match.
application = create_app(job_tasks={"example.task": lambda args: "ok"})

# Format code
poetry run black .
poetry run isort .

# Lint code
poetry run flake8 .

# Install pre-commit hooks
poetry run pre-commit install

# Commit with Commitizen
poetry run cz commit
```

## Coding Guidelines

- Follow the `Controller -> Service -> DAO -> Database` layering.
- Keep route handlers thin and move business logic into `service`.
- Keep database access inside `dao`.
- Use Pydantic for request and response schemas.
- Use SQLModel for database table models.
- Prefer `async/await` for async operations.
- Use Chinese docstrings for classes, functional methods, and important helpers; describe responsibilities and important side effects.
- Use Chinese inline comments for configuration constants, permission codes, cache keys, and lifecycle state.
- Use `Field(title=..., description=...)` for API fields, `description` for request parameters, and Chinese route `summary` values.
- Explain design reasons and cross-module constraints instead of restating obvious code. Update README, OpenAPI metadata, and test notes when behavior changes.
- Use Conventional Commits:

```text
feat: add user login
fix: handle redis timeout
refactor: simplify role service
docs: update readme
test: add user service tests
chore: update dependencies
```

## Seed Data

`assets/sql/fastapi-admin.sql` is a deployment-time seed script for initial users, roles, menus, permission catalog records, and role-menu relations. It is no longer executed from the application lifespan, which keeps startup read-only with respect to schema and seed data. The script uses `INSERT IGNORE`, so it can be rerun without duplicating existing primary-key records.

## FAQ

### 1. Missing environment variables on local startup

Make sure all required MySQL, Redis, and OSS variables are available in the process environment. Set `APP_ENV` to `development`, `staging`, or `production`; direct `uvicorn` startup can use the matching `.env.<APP_ENV>` file or process environment injection. Docker Compose should be started with `--env-file` pointing to the selected profile.

### 2. MySQL connection failed

Check:

- `MYSQL_HOST` and `MYSQL_POST`.
- Whether the database already exists.
- Username and password.
- Whether the MySQL container/service is running.

### 3. Redis authentication failed

Check:

- Whether `REDIS_PASSWORD` matches the Redis service.
- Whether Redis requires username authentication.
- Whether an empty `REDIS_USERNAME` matches your Redis configuration.

### 4. API returns 401

Make sure the request contains a valid token:

```http
Authorization: Bearer <access_token>
```

If the header is correct but the API still returns 401, also check:

- Whether the token still exists in memory or Redis.
- Whether Redis is reachable and `auth:token:` cache entries were not cleared.
- Whether `SECRET_KEY` stayed the same across restarts.
- Whether the token exceeded `ACCESS_TOKEN_EXPIRE_MINUTES`.

### 5. Requests are rate-limited

The default per-IP limit is `300/minute`, which permits concurrent admin-page requests. Username and phone login endpoints use `10/minute`, while captcha creation and verification use `30/minute`. Refresh-token, password-recovery, and external-auth endpoints have independent limits controlled by `RATE_LIMIT_REFRESH_TOKEN`, `RATE_LIMIT_PASSWORD_RESET`, and `RATE_LIMIT_EXTERNAL_AUTH`.

When one IP reaches `LOGIN_MAX_FAILED_ATTEMPTS` consecutive password failures within `LOGIN_IP_LOCK_SECONDS`, both username and phone login are blocked for `LOGIN_IP_LOCK_SECONDS`. The defaults are five failures and a 300-second lock. A correct password clears a failure counter that has not yet triggered a lock.

## Security and Operations

### Authentication and password policy

- Successful login returns a short-lived `access_token` and a rotating `refresh_token`. `POST /api/v1/user/token/refresh` consumes the old refresh token; reuse revokes the whole token family.
- Disabled users are rejected before token issuance. Protected routes also re-check user status, password version, and forced-password-change state.
- TOTP MFA is available through `POST /api/v1/user/mfa/setup`, `/api/v1/user/mfa/enable`, and `/api/v1/user/mfa/disable`. Login forms accept `mfa_code` or a one-time recovery code.
- `PASSWORD_*` settings control minimum length, character classes, password history, maximum age, and first-login password changes.
- Failed-login locking supports both IP and account dimensions through `LOGIN_MAX_FAILED_ATTEMPTS`, `LOGIN_IP_LOCK_SECONDS`, `LOGIN_ACCOUNT_MAX_FAILED_ATTEMPTS`, and `LOGIN_ACCOUNT_LOCK_SECONDS`.
- `POST /api/v1/user/password/forgot` and `/api/v1/user/password/reset` support email or SMS password recovery. Production must configure SMTP or an SMS webhook; recovery tokens are never returned in the response.
- Optional OIDC/OAuth and LDAP login use `/api/v1/auth/oidc/start`, `/api/v1/auth/oidc/callback`, and `/api/v1/auth/ldap/login` when the corresponding `OIDC_*` or `LDAP_*` settings are configured. OIDC requires `OIDC_ISSUER`, `OIDC_AUDIENCE`, and `OIDC_JWKS_URL`; callbacks validate the signature, issuer, audience, nonce, PKCE, and `email_verified`, and external login still requires an MFA code.

### Tenants and permissions

- Users, roles, menus, departments, posts, dictionaries, messages, files, jobs, configs, and logs carry `tenant_id`; reads and writes are filtered by the current tenant.
- Tenant members can switch tenant context through `/api/v1/tenant/switch`; missing tenant context fails closed for protected business queries.
- Mutating requests may send `Idempotency-Key`; batch user and role changes write before/after snapshots and request transactions roll back on failure.
- Startup synchronizes routes using `Auth.has_permission(...)` into `api_permission_catalog`.
- Field permissions use `field:<resource>:<field>` and are bound through the role DTO's `field_permission_codes`. Sensitive user fields are hidden when the actor lacks the field permission.
- Role and menu permission changes are recorded in `permission_change_versions` with actor, version, and before/after snapshots.

### Files, messages, and operations

- Files support signature detection, optional ClamAV scanning, OSS presigned URLs, local/OSS storage, chunked upload, and text redaction.
- When `FILE_VIRUS_SCAN_ENABLED=true`, provide a reachable ClamAV service and configure `CLAMAV_HOST`/`CLAMAV_PORT`; the default Compose file does not include a ClamAV container.
- The chunked upload flow is `POST /api/v1/file/chunk/init`, `PUT /api/v1/file/chunk/{upload_id}/{chunk_index}`, then `POST /api/v1/file/chunk/complete`. Incomplete chunk records and temporary directories are periodically removed according to `FILE_CHUNK_TTL_SECONDS`.
- System-config values of type `secret`, `password`, or `sensitive` are encrypted at rest and returned as a mask in list, detail, and value responses. Do not log sensitive values or commit them to environment examples.
- Text redaction is exposed through `GET /api/v1/file/redacted/{file_id}` and requires `FILE_REDACTION_ENABLED=true`.
- Users, roles, and dictionaries support Excel import/export. Imports still apply DTO validation, password policy, tenant checks, and duplicate checks.
- Users, roles, and dictionaries also support persistent asynchronous exports: call `/export/async`, poll `/export/tasks/{task_id}`, and download from `/export/tasks/{task_id}/download` after completion.
- Message management pagination supports title, content, type, status, and publish-time range filters. Personal messages use `GET /api/v1/message/my/list` with keyword, type, read-status, and time-range filters.
- Message API date-time values use `YYYY-MM-DD HH:mm:ss`, and personal messages exclude items whose publish time is later than the current UTC+8 time.
- `GET /api/v1/message/latest` returns up to the five newest system, approval, and alarm messages in separate groups. `GET /api/v1/message/unread-count`, `POST /api/v1/message/{message_id}/read`, and `POST /api/v1/message/read-all` provide unread and read-state operations.
- New and updated messages accept only `system`, `approval`, or `alarm` for `message_type`. Messages support in-app, webhook, email, and SMS delivery. External delivery failures use a database-backed lease plus bounded exponential backoff using `NOTIFICATION_DELIVERY_LEASE_SECONDS`, `NOTIFICATION_RETRY_MAX_ATTEMPTS`, and `NOTIFICATION_RETRY_BASE_SECONDS`.
- Database backups can be created with `poetry run python -m scripts.backup_database backup` or the platform-super-admin-protected `/api/v1/ops/backup/create` endpoint. Run `poetry run python -m scripts.backup_database verify <filename>` or `/api/v1/ops/backup/verify` before `poetry run python -m scripts.backup_database rehearse <filename>` or `/api/v1/ops/backup/rehearse`; rehearsal imports into `BACKUP_REHEARSAL_DATABASE` and removes it afterward. Online restore is disabled by default and requires an explicit maintenance window, operations token, and MFA reauthentication. Backups are Fernet-encrypted and cleaned up according to the retention policy.

### Jobs and observability

- APScheduler triggers jobs. With `SCHEDULER_WORKER_MODE=queue`, jobs are published to Redis Streams and executed by the independent `fastapi-worker` service. The Worker exposes a heartbeat, claims idle messages, and renews the task lock during long execution.
- A Redis `SET NX EX` lock prevents duplicate execution across instances. Jobs support timeout, retry, pause/resume, and execution logs.
- `SCHEDULER_DEFAULT_TIMEOUT_SECONDS`, `SCHEDULER_LOCK_TTL_SECONDS`, and `SCHEDULER_DEFAULT_MAX_RETRIES` define defaults; individual job DTOs can override timeout and retries.
- `/metrics` exposes HTTP metrics plus MySQL/Redis readiness, job executions/durations, and alert delivery state. Configure `ALERT_WEBHOOK_URL` to send structured job-failure alerts.
- Set `OTEL_ENABLED=true` and `OTEL_EXPORTER_OTLP_ENDPOINT` to export FastAPI traces over OTLP. Log files are retained according to `LOG_RETENTION_DAYS`. Outside development, `/docs`, `/redoc`, `/openapi.json`, and `/metrics` require `DOCS_AUTH_TOKEN` or `METRICS_AUTH_TOKEN`.

### Migrations and Docker troubleshooting

The current migration head is `0025_security_consistency`. The migration entrypoint creates or expands `alembic_version.version_num` to `VARCHAR(64)`, which handles older databases created with Alembic's default `VARCHAR(32)`. Check that `/api/v1/health/ready` reports `schema=ok` after deployment.

```bash
docker compose --env-file .env.development up -d --build
docker compose --env-file .env.development logs -f fastapi-migrate
poetry run python -m scripts.migrate_database
```

An `1045 Access denied` error means the credentials in the persistent MySQL volume differ from the selected environment file. A volume does not rotate passwords when `.env` changes: preserve data by rotating `fastapi_app` with the original root password; only use `docker compose down -v` for disposable development data. Never delete a production volume to resolve `1045`.

## License

No license is declared in this repository yet. Add one before public release or commercial use.
