import globals from 'globals'
import tseslint from 'typescript-eslint'
import pluginVue from 'eslint-plugin-vue'
import json from '@eslint/json'
import css from '@eslint/css'
import { defineConfig } from 'eslint/config'

const typedFiles = [
  'src/**/*.{js,mjs,cjs,ts,mts,cts,vue}',
  '*.config.{js,mjs,cjs,ts}',
  'vite.config.*',
  'vitest.config.*',
  'eslint.config.*',
  'scripts/**/*.{js,mjs,cjs,ts,mts,cts}',
]

export default defineConfig([
  {
    ignores: [
      '**/node_modules/**',
      '**/dist/**',
      '**/coverage/**',
      '**/*.d.ts',
      '**/tsconfig*.json',
    ],
  },
  {
    files: ['src/**/*.{js,mjs,cjs,ts,mts,cts,vue}'],
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.es2025,
      },
    },
  },
  {
    files: [
      '*.config.{js,mjs,cjs,ts}',
      'vite.config.*',
      'vitest.config.*',
      'eslint.config.*',
      'scripts/**/*.{js,mjs,cjs,ts,mts,cts}',
    ],
    languageOptions: {
      globals: {
        ...globals.node,
        ...globals.es2025,
      },
    },
  },
  ...tseslint.configs.recommended.map((config) => ({
    ...config,
    files: typedFiles,
  })),
  ...pluginVue.configs['flat/essential'].map((config) => ({
    ...config,
    files: ['src/**/*.vue'],
  })),
  {
    files: ['**/*.vue'],
    languageOptions: {
      parserOptions: {
        parser: tseslint.parser,
      },
    },
  },
  { files: ['**/*.json'], plugins: { json }, language: 'json/json' },
  { files: ['**/*.css'], plugins: { css }, language: 'css/css' },
])
