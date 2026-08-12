# FastAPI Admin Vue

FastAPI Admin Vue is the enterprise administration frontend for FastAPI Admin. Built with Vue 3, TypeScript, Vite, and Naive UI, it provides a consistent session, dynamic routing, permission menu, administration workspace, preference, internationalization, and navigation-feedback layer over versioned FastAPI HTTP APIs.

> The frontend owns interaction and permission presentation. FastAPI remains the authority for authentication, authorization, tenancy, data scope, business state, and data consistency.

中文文档：[README.md](./README.md)

## 1. Project Scope

The project targets enterprise back offices, internal operations platforms, and multi-tenant administration systems. Its engineering priorities are:

- **Explicit contracts**: business requests use domain API modules and dedicated TypeScript types; views do not call the transport client directly.
- **Complete permission flow**: the server supplies routes and permission codes, the frontend controls presentation, and the backend performs final authorization.
- **Consistent experience**: layout, tabs, breadcrumbs, search forms, tables, feedback, themes, and loading behavior follow shared conventions.
- **Clear ownership**: views, shared components, hooks, stores, APIs, and utilities have distinct responsibilities.
- **Verifiable delivery**: type checking, code linting, style linting, formatting, tests, and production builds are mandatory quality gates.

## 2. Capabilities

| Domain                     | Implemented capabilities                                                                                                   |
| -------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| Authentication and session | Username login, CAPTCHA, token refresh, sign-out, password change, and expired-session handling                            |
| Routing and permissions    | Server routes, local component allowlist, authentication guards, permission-code controls, and merged static/dynamic menus |
| Identity and organization  | Users, roles, menus, departments, posts, role-menu permissions, and data-scope configuration                               |
| Reference data             | Dictionary types, dictionary data, import/export, and dictionary display components                                        |
| Message center             | Message administration, user inbox, unread counts, read state, and header entry point                                      |
| Monitoring                 | Login, operation, and exception logs; online sessions and forced sign-out                                                  |
| Scheduled jobs             | Pagination, details, create, update, delete, run now, and execution logs                                                   |
| Application experience     | Tabs, KeepAlive, theme and layout preferences, Chinese/English, timezone, watermark, update detection, and route loading   |
| Shared foundation          | Standard forms, search forms, file-selection/upload interaction, pagination, ECharts, Lottie, and utilities                |

Page availability depends on server-provided menus, current permissions, and the backend capabilities deployed in the target environment. A scheduled job `task_name` must match a handler registered by the backend; the UI does not expose arbitrary code execution.

## 3. Technology Stack

| Category                 | Technology                                                      |
| ------------------------ | --------------------------------------------------------------- |
| Core                     | Vue 3, `<script setup lang="ts">`, TypeScript Strict Mode       |
| Tooling                  | Vite, pnpm, Sass, UnoCSS                                        |
| Routing and state        | Vue Router, Pinia, `pinia-plugin-persistedstate`                |
| UI and icons             | Naive UI, Ionicons 5, SVG icons                                 |
| HTTP                     | Alova Fetch Adapter                                             |
| Visualization and motion | ECharts, Lottie Web                                             |
| Quality                  | Vitest, Vue Test Utils, ESLint, Stylelint, Prettier, Commitlint |

The supported Node.js range is declared in `package.json` and is currently `^22.18.0 || >=24.12.0`. The project uses pnpm.

## 4. Architecture

```text
View / Layout / Component
           │
           ├── Hook / Pinia Store
           │
           └── Domain API ── Response Parser
                              │
                         Request Transport
                              │
                         /api/v1 (FastAPI)
```

Primary runtime flow:

1. After login, the authentication store loads the current user and `GET /api/v1/user/routes`.
2. The dynamic-route converter validates paths, names, metadata, and local component mappings.
3. Valid routes are registered under the `app` layout; the sidebar combines server routes with static menus.
4. Views call the backend through `src/api/<domain>/`; parsers validate `unknown` response data into domain types.
5. The transport layer owns common responses, 401 refresh, session versions, error feedback, and file responses.

### Directory Structure

```text
src/
├── api/                    # Domain APIs, request parameters, and response parsers
├── assets/                 # Global styles and static assets such as Lottie data
├── components/             # Cross-page components and application-shell components
├── hooks/                  # Vue, Router, Pinia, DOM, and third-party orchestration
├── layouts/BasicLayout/    # Sidebar, header, tabs, content, and footer
├── router/                 # Static routes, guards, dynamic routes, and cache rules
├── stores/modules/         # Authentication, tabs, preferences, and route loading
├── types/                  # API, route, store, transport, and component types
├── utils/                  # Pure utilities, transport boundary, guards, and infrastructure
├── views/                  # Route-level business views
└── __tests__/              # Vitest unit and component tests
```

## 5. Local Development

### Prerequisites

- Node.js `^22.18.0 || >=24.12.0`
- pnpm
- A reachable FastAPI Admin service, defaulting to `http://127.0.0.1:3000` in development

### Start the Application

```sh
pnpm install
pnpm dev
```

The default URL is `http://127.0.0.1:5173`. `pnpm dev` runs the complete static check before starting Vite.

Development requests under `/api` are proxied to `http://127.0.0.1:3000` by default. Create `.env.local` from `.env.example` to override local public configuration. Every `VITE_*` value is included in the browser bundle; never store passwords, tokens, secrets, or internal credentials in these files.

### Environment Variables

| Variable                 | Description                         | Default example         |
| ------------------------ | ----------------------------------- | ----------------------- |
| `VITE_APP_TITLE`         | Application title and footer name   | `FastAPI Admin`         |
| `VITE_API_BASE_URL`      | Browser API base path               | `/api/v1`               |
| `VITE_API_PROXY_TARGET`  | Development proxy target            | `http://127.0.0.1:3000` |
| `VITE_API_PROXY_ENABLED` | Enable the `/api` development proxy | `true`                  |
| `VITE_DEV_HOST`          | Development server host             | `127.0.0.1`             |
| `VITE_DEV_PORT`          | Development server port             | `5173`                  |
| `VITE_DEV_OPEN`          | Open a browser after startup        | `false`                 |
| `VITE_PREVIEW_HOST`      | Preview server host                 | `127.0.0.1`             |
| `VITE_PREVIEW_PORT`      | Preview server port                 | `4173`                  |
| `VITE_BASE_PATH`         | Deployment base path                | `/`                     |
| `VITE_SOURCEMAP`         | Generate source maps                | `false`                 |

The project does not use `VITE_ROUTE_MODE`. Authenticated business routes always come from the backend.

## 6. API and Session Contract

Business APIs are imported from `@/api` or a specific domain API module. Views and shared components must not create Alova or Fetch requests directly.

The common response shape is:

```ts
interface ApiResponse<T> {
  code: number
  error_code?: string | null
  message: string
  data: T
}
```

Transport rules:

- The default API base path is `/api/v1`.
- Domain responses enter the boundary as `unknown` and are validated by parsers.
- A 401 response uses one shared refresh attempt; a failed refresh clears the active session.
- General failures use the global Message bridge; login and sign-out use Notification.
- File downloads use a dedicated Blob path and do not require the JSON envelope.
- A new endpoint requires synchronized request types, response types, parser, caller, and focused tests.

## 7. Routing, Permissions, and Cache

Static routes live in `src/router/modules/` and cover login, password change, system settings, component demos, and default error pages. Authenticated business routes are loaded from `GET /api/v1/user/routes` and registered under `BasicLayout`.

Server `component` values can only resolve through the local `src/views/**/*.vue` allowlist. Routes with missing components, invalid paths, or conflicting names are rejected; server strings never trigger unrestricted dynamic imports.

Permission principles:

- Route guards own session-aware navigation behavior.
- `v-permission`, permission hooks, and action controls own frontend visibility.
- The backend must validate the user, tenant, permission code, and data scope again.
- A hidden frontend control is not a security boundary.

Routes with `meta.noCache === false` may use KeepAlive under `RouteTab_<route-key>`. Tab state is persisted in `sessionStorage`; the tab list and component cache remain separate states.

## 8. Layout, Theme, and Loading

`BasicLayout` contains the sidebar, header, tabs, content area, and footer. It supports three scroll modes:

| Mode        | Behavior                                                                    |
| ----------- | --------------------------------------------------------------------------- |
| `content`   | Header, tabs, and sidebar stay fixed; only content scrolls internally       |
| `workspace` | The complete right workspace scrolls                                        |
| `sticky`    | Header and tabs remain sticky while the rest of the right workspace scrolls |

System settings centrally manage light, dark, or system theme; accent color; radius; font size; color-weak and grayscale modes; content width; layout visibility; Chinese/English; timezone; watermark; and navigation feedback. Preferences are persisted in `localStorage`.

Route loading has two overlay scopes:

- `GlobalLoading` covers initial navigation and navigation outside the application layout.
- `ContentLoading` covers the stable right-workspace viewport for navigation within `BasicLayout`. Its size is independent of business-page height, so long and empty pages cannot stretch or collapse the overlay.
- `RouterLoadingBar` provides top-level progress feedback.

`pageTransition` controls the loading bar, while `loadingAnimation` controls Lottie overlays. Disabling animation hides visual feedback without changing navigation completion state.

Production builds emit a same-origin `version.json`. When update checks are enabled, the application compares build IDs and presents a refresh prompt after detecting a new version; a full reload occurs only after user confirmation.

## 9. Development Conventions

### Module Ownership

| Type       | Directory                               | Responsibility                                                         |
| ---------- | --------------------------------------- | ---------------------------------------------------------------------- |
| Shared UI  | `src/components/`                       | Rendering, interaction, Props, Emits, Slots, and local validation      |
| Page UI    | `src/views/<domain>/<page>/components/` | Presentation and interaction for one business page                     |
| Hook       | `src/hooks/use*.ts`                     | Vue lifecycle, Router, Pinia, DOM, and third-party instance management |
| Store      | `src/stores/modules/`                   | Cross-page sessions, tabs, preferences, and shared state               |
| Domain API | `src/api/<domain>/`                     | Backend calls, parameter conversion, and response parsing              |
| Utility    | `src/utils/`                            | Lifecycle-free pure logic and explicit infrastructure boundaries       |

Shared components communicate through Props, Emits, `v-model`, or Slots and do not call domain APIs. Every listener, subscription, observer, timer, and third-party instance must have a cleanup path.

Detailed conventions:

- [Shared component conventions](./src/components/README.md)
- [Hook guide](./src/hooks/README.md)
- [Utility guide](./src/utils/README.md)
- [Frontend engineering rules](./.codex/README.md)

## 10. Quality Gates

```sh
pnpm run type-check       # TypeScript and Vue type checking
pnpm run lint             # ESLint
pnpm run lint:style       # Stylelint
pnpm run format:check     # Prettier
pnpm run test:run         # Full static checks and Vitest
pnpm run build            # Full static checks and production build
git diff --check          # Whitespace validation
```

Focused test example:

```sh
pnpm exec vitest run src/__tests__/BasicLayout.spec.ts src/__tests__/Lottie.spec.ts
```

On Windows, Vite or Vitest may report `spawn EPERM`. Retry the runtime command in a terminal that allows child processes and report static checks, tests, and builds separately.

## 11. Build and Deployment

| Command                      | Mode        | Output              |
| ---------------------------- | ----------- | ------------------- |
| `pnpm run build:development` | development | `dist-development/` |
| `pnpm run build:staging`     | staging     | `dist-staging/`     |
| `pnpm run build`             | production  | `dist/`             |

Deployment requirements:

- The web server must support SPA History fallback and return `index.html` for unknown frontend paths.
- Reverse-proxy `/api` to FastAPI, or configure `VITE_API_BASE_URL` to a reachable address.
- `VITE_BASE_PATH` must match the deployed subpath.
- Serve `version.json` with no caching or a short cache lifetime; hashed static assets can use long-lived caching.
- Production source maps are disabled by default. Evaluate source-exposure risk before enabling them.

## 12. Security Boundaries

- Never store passwords, tokens, CAPTCHA values, MFA values, secrets, or production data in source code, environment files, logs, URLs, screenshots, or test fixtures.
- Treat all server data as untrusted and validate it through types and runtime guards.
- Menus, buttons, and route guards improve the experience but never replace backend authorization.
- Server routes can resolve only to the local View allowlist.
- When users explicitly enable “remember login,” the existing implementation stores credentials in `localStorage`. This is a known security risk; new features must not expand it, and replacement belongs in a dedicated security change.

## 13. Engineering Documentation

Repository facts and execution rules are maintained under `.codex/`:

- `AGENTS.md`: mandatory frontend implementation rules.
- `PROJECT.md`: current project facts, scripts, environment, and APIs.
- `ARCHITECTURE.md`: module ownership and runtime data flow.
- `BOUNDARY.md`: scope, security constraints, and forbidden responsibilities.
- `WORKFLOW.md`: analysis, implementation, verification, and delivery workflow.
