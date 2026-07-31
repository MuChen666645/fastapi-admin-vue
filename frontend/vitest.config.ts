import { defineConfig, mergeConfig } from 'vitest/config'

import { createViteConfig } from './vite.config'

export default mergeConfig(
  createViteConfig({ command: 'serve', mode: 'test' }),
  defineConfig({
    test: {
      environment: 'jsdom',
      clearMocks: true,
      restoreMocks: true,
      passWithNoTests: true,
      setupFiles: ['./src/__tests__/setup.ts'],
      exclude: ['node_modules/**', 'dist/**', 'dist-*/**', 'coverage/**', 'e2e/**'],
    },
  }),
)
