import path from 'node:path'
import { fileURLToPath, URL } from 'node:url'

import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { NaiveUiResolver } from 'unplugin-vue-components/resolvers'
import UnoCSS from 'unocss/vite'
import { defineConfig, loadEnv, type ConfigEnv, type Plugin, type UserConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import vueDevTools from 'vite-plugin-vue-devtools'
import svgLoader from 'vite-svg-loader'
import { createSvgIconsPlugin } from 'vite-plugin-svg-icons'

const frontendRoot = fileURLToPath(new URL('.', import.meta.url))
const sourceRoot = fileURLToPath(new URL('./src', import.meta.url))
const defaultHost = '127.0.0.1'
const buildOutputDirs: Record<string, string> = {
  development: 'dist-development',
  production: 'dist',
  staging: 'dist-staging',
}
const appUpdateManifestFile = 'version.json'

const buildMinifyOptions = {
  compress: {
    dropConsole: true,
    dropDebugger: true,
  },
  mangle: true,
  codegen: {
    removeWhitespace: true,
    legalComments: 'none',
  },
} as const

const readBoolean = (value: string | undefined, fallback: boolean): boolean => {
  const normalizedValue = value?.trim().toLowerCase()

  if (normalizedValue === undefined) {
    return fallback
  }

  return normalizedValue === 'true'
}

const readPort = (value: string | undefined, fallback: number): number => {
  const port = Number(value)
  return Number.isInteger(port) && port > 0 && port <= 65535 ? port : fallback
}

const readBasePath = (value: string | undefined): string => {
  const basePath = value?.trim()

  if (!basePath || basePath === '/') {
    return '/'
  }

  return `/${basePath.replace(/^\/+|\/+$/g, '')}/`
}

const getBuildOutputDir = (mode: string): string => {
  return path.resolve(frontendRoot, buildOutputDirs[mode] ?? 'dist')
}

const createApiProxy = (target: string | undefined, enabled: boolean) => {
  const proxyTarget = target?.trim()

  if (!enabled || !proxyTarget) {
    return undefined
  }

  return {
    '/api': {
      target: proxyTarget,
      changeOrigin: true,
    },
  }
}

const manualChunks = (id: string): string | undefined => {
  const normalizedId = id.replaceAll('\\', '/')

  if (
    normalizedId.includes('/node_modules/vue/') ||
    normalizedId.includes('/node_modules/vue-router/') ||
    normalizedId.includes('/node_modules/pinia/')
  ) {
    return 'vue'
  }

  return normalizedId.includes('/node_modules/naive-ui/') ? 'naive' : undefined
}

const createAppUpdateManifestPlugin = (buildId: string): Plugin => ({
  name: 'app-update-manifest',
  apply: 'build',
  generateBundle() {
    this.emitFile({
      type: 'asset',
      fileName: appUpdateManifestFile,
      source: `${JSON.stringify({ buildId, builtAt: new Date().toISOString() }, null, 2)}\n`,
    })
  },
})

export const createViteConfig = ({ command, mode, isPreview = false }: ConfigEnv): UserConfig => {
  const env = loadEnv(mode, frontendRoot, 'VITE_')
  const isTest = mode === 'test'
  const isDevelopmentServer = command === 'serve' && !isPreview
  const apiProxyEnabled = readBoolean(env.VITE_API_PROXY_ENABLED, command === 'serve' && !isTest)
  const apiProxy = createApiProxy(env.VITE_API_PROXY_TARGET, apiProxyEnabled)
  const basePath = readBasePath(env.VITE_BASE_PATH)
  const sourcemap = readBoolean(env.VITE_SOURCEMAP, false)
  const buildId = command === 'build' ? `build-${Date.now().toString(36)}` : 'development'

  return {
    base: basePath,
    define: {
      __APP_BUILD_ID__: JSON.stringify(buildId),
    },
    plugins: [
      vue(),
      vueJsx(),
      ...(!isTest
        ? [
            UnoCSS(),
            AutoImport({
              imports: [
                'vue',
                'vue-router',
                {
                  'naive-ui': ['useDialog', 'useMessage', 'useNotification', 'useLoadingBar'],
                },
              ],
              dts: path.resolve(frontendRoot, 'auto-imports.d.ts'),
            }),
            createSvgIconsPlugin({
              iconDirs: [path.resolve(frontendRoot, 'src/icons')],
              symbolId: 'icon-[dir]-[name]',
              inject: 'body-last',
              customDomId: '__svg__icons__dom__',
            }),
            Components({
              dts: path.resolve(frontendRoot, 'components.d.ts'),
              resolvers: [NaiveUiResolver()],
            }),
            createAppUpdateManifestPlugin(buildId),
          ]
        : []),
      ...(isDevelopmentServer && !isTest ? [vueDevTools()] : []),
      svgLoader(),
    ],
    resolve: {
      alias: {
        '@': sourceRoot,
      },
    },
    server: {
      host: env.VITE_DEV_HOST?.trim() || defaultHost,
      port: readPort(env.VITE_DEV_PORT, 5173),
      open: readBoolean(env.VITE_DEV_OPEN, false),
      strictPort: true,
      proxy: apiProxy,
    },
    preview: {
      host: env.VITE_PREVIEW_HOST?.trim() || env.VITE_DEV_HOST?.trim() || defaultHost,
      port: readPort(env.VITE_PREVIEW_PORT, 4173),
      strictPort: true,
      proxy: apiProxy,
    },
    build: {
      outDir: getBuildOutputDir(mode),
      minify: 'oxc',
      sourcemap,
      reportCompressedSize: false,
      chunkSizeWarningLimit: 2048,
      rolldownOptions: {
        output: {
          manualChunks,
          minify: buildMinifyOptions,
          comments: {
            legal: false,
            annotation: false,
            jsdoc: false,
          },
        },
      },
    },
  }
}

export default defineConfig(createViteConfig)
