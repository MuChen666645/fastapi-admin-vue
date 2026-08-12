# FastAPI Admin Vue Frontend

This is the Vue 3 administration frontend for FastAPI Admin. It owns the session experience, server-provided menu routes, management pages, tabs, theme, preferences, and route-loading feedback. FastAPI remains the authority for authentication, authorization, tenancy, data scope, and business state.

Chinese documentation: [README.md](./README.md).

## Stack

- Vue 3 with `<script setup lang="ts">` and strict TypeScript
- Vite, Vue Router, and Pinia
- Alova fetch adapter and Naive UI
- UnoCSS reset, Sass, and Ionicons 5
- Lottie Web, Vitest, Vue Test Utils, ESLint, Stylelint, and Prettier

Use pnpm. The supported Node range is declared in `package.json`.

## Quick start

```sh
pnpm install
pnpm dev
```

The default development URL is `http://127.0.0.1:5173`. `pnpm dev` runs `pnpm run check` before starting Vite. In development, `/api` is proxied to `http://127.0.0.1:3000`. Copy `.env.example` to `.env.local` when the FastAPI service uses another address. Never put secrets, tokens, or internal credentials in frontend environment files.

## Environment

| Variable                                          | Purpose                    | Example                      |
| ------------------------------------------------- | -------------------------- | ---------------------------- |
| `VITE_APP_TITLE`                                  | HTML title and footer name | `FastAPI Admin`              |
| `VITE_API_BASE_URL`                               | Browser API base path      | `/api/v1`                    |
| `VITE_API_PROXY_TARGET`                           | Development proxy target   | `http://127.0.0.1:3000`      |
| `VITE_API_PROXY_ENABLED`                          | Enable the `/api` proxy    | `true` / `false`             |
| `VITE_DEV_HOST`, `VITE_DEV_PORT`, `VITE_DEV_OPEN` | Development server options | `127.0.0.1`, `5173`, `false` |
| `VITE_PREVIEW_HOST`, `VITE_PREVIEW_PORT`          | Preview server options     | `127.0.0.1`, `4173`          |
| `VITE_BASE_PATH`                                  | Deployment base path       | `/`                          |
| `VITE_SOURCEMAP`                                  | Generate source maps       | `false`                      |

The frontend does not use `VITE_ROUTE_MODE`. Authenticated business routes always come from `GET /api/v1/user/routes`.

## Routes and permissions

- `/login` is public.
- `/change-password` is the authenticated password-change page.
- `/` mounts `BasicLayout`.
- `/system/settings` is the static system preferences entry, named `system-settings` and hidden from the server menu.
- `/demo/default-pages` is an authenticated static menu tree: `Demo / Default pages / 403, 404, 500, Offline`. It is shown in the frontend sidebar.
- `/403`, `/500`, `/offline`, and the not-found route provide default error pages with refresh and home actions.

After login, the frontend loads `GET /api/v1/user/routes` and registers validated business routes under the `app` layout. Server `component` values are resolved through the local `src/views/**/*.vue` allowlist. Frontend menus and route guards improve the experience but never replace backend authorization.

The server-provided online-users page lists active login sessions within the operator's data scope, with username and login-IP filters. The `monitor:online:forceLogout` permission enables confirmed actions to sign out one session or every visible session for a user.

## Project structure

```text
src/
├── api/                 # Domain API functions and response parsers
├── components/          # Shared forms, loading, request Message bridge, breadcrumbs, and overlays
├── hooks/               # Theme, locale, title, Lottie, ECharts, and route cache behavior
├── layouts/BasicLayout/ # Sidebar, header, tabs, content, and footer
├── router/              # Static routes, guards, and dynamic route conversion
├── stores/modules/      # Auth, tabs, route loading, and preferences
├── types/               # API, route, store, transport, and preference types
├── utils/               # Public toolkit, request boundary, locale dictionary, and Lottie helpers
├── views/               # Route-level pages
└── __tests__/           # Vitest component and unit tests
```

Page-specific areas belong under the page directory, such as `src/views/system/config/components/`. Shared components belong under `src/components/`. Keep all TypeScript declarations in `src/types/` and import them through `@/types`.

Component documentation is indexed in [`src/components/README.md`](./src/components/README.md). Hook usage is documented in [`src/hooks/README.md`](./src/hooks/README.md), and the public utility toolkit is documented in [`src/utils/README.md`](./src/utils/README.md).

The default-pages demo is a nested route tree in `src/router/modules/protected.ts`; its four leaf routes reuse the 403, 404, 500, and offline views under `src/views/error/`.

## Components, Utilities, and Hooks

Choose the location by dependency:

| Need                       | Directory                               | Owns                                                                 | Must not own                                                                  |
| -------------------------- | --------------------------------------- | -------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| Shared UI                  | `src/components/`                       | Rendering, interaction, Props/Emits, slots, and local validation     | Domain API calls, business lists, tokens, or cross-page business state        |
| Page-specific UI           | `src/views/<domain>/<page>/components/` | Display and interaction for one page                                 | Direct reuse by unrelated pages or duplicate shared primitives                |
| Lifecycle/context behavior | `src/hooks/use*.ts`                     | Vue lifecycle, Router, Pinia, DOM refs, and third-party instances    | Domain API calls, response parsing, or business submission                    |
| Lifecycle-free logic       | `src/utils/`                            | Pure calculation, formatting, parsing, conversion, and safety checks | Hidden global state, page effects, or undocumented business mutations         |
| Cross-page business state  | `src/stores/modules/`                   | Session, tabs, preferences, and loading state                        | DOM access, page-component dependencies, or backend authorization replacement |

Components communicate through Props, Emits, `v-model`, or slots. A form or search component validates locally first, then the page or Store calls a verified API from `@/api`. Every shared component needs a directory README and public-behavior tests covering its contract, validation, loading, duplicate-submission handling, and cleanup behavior.

Hooks use the `use` naming convention and are reserved for Vue, Router, Pinia, DOM, or lifecycle context. Every listener, subscription, observer, timer, and third-party instance must have a cleanup path. Utilities should have explicit inputs, outputs, errors, and side effects; reusable functions are exported from `@/utils`, while request transport, response guards, storage, and feedback bridges keep their specific module entry points.

See the detailed [component conventions](./src/components/README.md), [Hook guide](./src/hooks/README.md), [utility guide](./src/utils/README.md), and [Codex documentation index](./.codex/README.md).

## Preferences and bilingual mode

The `/system/settings` page uses one `usePreferencesStore` persisted in `localStorage`.

- Appearance: light, dark, or system theme; accent color; corner radius; font size; color-weak and grayscale modes.
- Layout: full-width or centered content; sidebar, tabs, breadcrumbs, footer; and content scroll behavior.
- General: `zh-CN` / `en-US`, timezone, dynamic document titles, watermark, update-check intent, and loading feedback.

The content scroll modes are:

- `content`: header, tabs, and sidebar stay fixed while the content area scrolls internally.
- `workspace`: the entire right workspace scrolls with the page.

The app header and login-page toolbar include a language toggle, so users can switch between `zh-CN` and `en-US` without opening system settings. Dashboard cards, charts, and activity copy follow the selected preference.

- `sticky`: only the header and tabs stay fixed while the remaining right-side content scrolls.

Language changes apply immediately to the settings page and shared shell. Static route titles use the local dictionary; unknown server-provided titles remain unchanged. The update-check switch currently stores user intent only. A real update manifest URL, version format, and error contract must be supplied before update requests are added. Copying preferences exports UI settings only and never session credentials.

## API and session

API calls go through `src/api/<domain>/index.ts` and `src/utils/request.ts`. Current auth endpoints are:

```text
POST /user/login/username
POST /user/login/phone
GET  /captcha/image
POST /user/token/refresh
POST /user/logout
PUT  /user/me/password
GET  /user/info
GET  /user/routes
```

The transport validates the common `{ code, error_code?, message, data }` response, handles authorization, and performs one shared refresh attempt for 401 responses with session-version protection. General request failures are shown through Naive UI Message, while login and sign-out use Notification. Parsers validate unknown response data before it reaches a Store or page.

## Loading, tabs, and cache

- `GlobalLoading` covers initial and layout-external navigation.
- `ContentLoading` covers content-only navigation inside `BasicLayout`.
- `RouterLoadingBar` shows the Naive UI top progress bar.
- `pageTransition` controls the top progress bar, while `loadingAnimation` controls both Lottie overlays.
- `meta.noCache === false` enables KeepAlive with a `RouteTab_<route-key>` cache name.
- `useTabsStore` persists tab state in `sessionStorage`; tab state and component cache are separate concerns.

## Commands

```sh
pnpm run check
pnpm run test:run
pnpm run build
pnpm run build:staging
pnpm run preview
git diff --check
```

For a focused test:

```sh
pnpm exec vitest run src/__tests__/SystemConfig.spec.ts
```

On Windows, Vite or Vitest may report `spawn EPERM`. Retry the runtime command in an environment that permits child processes and report static checks separately from runtime tests.

## Security boundaries

- Never write tokens, passwords, CAPTCHA values, MFA values, reset tokens, or production data to logs, URLs, source files, screenshots, or test output.
- Server routes are resolved only through the local component allowlist.
- Backend authorization remains authoritative.
- The existing “remember login” flow stores credentials in `localStorage` when explicitly enabled; this is a known risk and new features must not expand it.

## Codex documentation

Frontend-specific rules and facts are in `.codex/`:

- `AGENTS.md`: implementation rules.
- `PROJECT.md`: verified project facts, scripts, environment, and API.
- `ARCHITECTURE.md`: module responsibilities and runtime data flow.
- `BOUNDARY.md`: scope, security, and forbidden responsibilities.
- `WORKFLOW.md`: analysis, implementation, verification, and delivery flow.
