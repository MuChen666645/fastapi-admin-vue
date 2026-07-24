import { chmodSync, existsSync, mkdirSync, writeFileSync } from 'node:fs'
import { execFileSync } from 'node:child_process'
import { resolve } from 'node:path'

const frontendRoot = process.cwd()
const parentRoot = resolve(frontendRoot, '..')
let repositoryRoot = null
let isMonorepo = false

if (existsSync(resolve(parentRoot, '.git'))) {
  repositoryRoot = parentRoot
  isMonorepo = true
} else if (existsSync(resolve(frontendRoot, '.git'))) {
  repositoryRoot = frontendRoot
}

const projectRoot = repositoryRoot ?? frontendRoot
const hooksDirectory = resolve(projectRoot, '.githooks')
const frontendCommand = isMonorepo ? 'cd frontend && ' : ''

const hookHeader = `#!/bin/sh

if [ "$SKIP_GIT_HOOKS" = "1" ]; then
    echo "[INFO] Git hooks skipped because SKIP_GIT_HOOKS is set."
    exit 0
fi

`

const hooks = {
  'pre-commit': isMonorepo
    ? `${hookHeader}frontend_changed=false
for file in $(git diff --cached --name-only --diff-filter=ACMR); do
  case "$file" in
    frontend/*) frontend_changed=true; break ;;
  esac
done
if [ "$frontend_changed" = "true" ]; then
  ${frontendCommand}pnpm exec lint-staged --relative && pnpm run lint && pnpm run lint:style
fi
`
    : `${hookHeader}if [ -n "$(git diff --cached --name-only --diff-filter=ACMR)" ]; then
  ${frontendCommand}pnpm exec lint-staged --relative && pnpm run lint && pnpm run lint:style
fi
`,
  'commit-msg': `${hookHeader}${frontendCommand}pnpm exec commitlint --edit "$1"\n`,
}

mkdirSync(hooksDirectory, { recursive: true })
for (const [hookName, hookContent] of Object.entries(hooks)) {
  const hookPath = resolve(hooksDirectory, hookName)
  writeFileSync(hookPath, hookContent, 'utf8')
  chmodSync(hookPath, 0o755)
}

if (!repositoryRoot) {
  process.exit(0)
}

try {
  let hooksPath = ''
  try {
    hooksPath = execFileSync('git', ['config', '--local', '--get', 'core.hooksPath'], {
      cwd: repositoryRoot,
      encoding: 'utf8',
    }).trim()
  } catch (error) {
    if (error.status !== 1) {
      console.warn('[WARN] Git hooks were not installed; dependency installation will continue.')
      process.exit(0)
    }
  }

  if (hooksPath !== '../.githooks') {
    execFileSync('git', ['config', '--local', 'core.hooksPath', '../.githooks'], {
      cwd: repositoryRoot,
      stdio: 'inherit',
    })
  }
} catch {
  console.warn('[WARN] Git hooks were not installed; dependency installation will continue.')
}
