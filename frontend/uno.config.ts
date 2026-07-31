import { defineConfig, presetWind3 } from 'unocss'

import { unoShortcuts } from './src/styles/uno-shortcuts'

export default defineConfig({
  presets: [presetWind3()],
  shortcuts: unoShortcuts,
  safelist: [
    'summary-change--positive',
    'summary-change--negative',
    'summary-change--warning',
    'quick-action-icon--blue',
    'quick-action-icon--purple',
    'quick-action-icon--pink',
    'quick-action-icon--green',
    'quick-action-icon--yellow',
    'quick-action-icon--gray',
    'theme-preview--light',
    'theme-preview--dark',
    'theme-preview--system',
    'accent-swatch--blue',
    'accent-swatch--violet',
    'accent-swatch--rose',
    'accent-swatch--amber',
    'accent-swatch--green',
    'accent-swatch--slate',
  ],
  content: {
    pipeline: {
      include: [/\.(vue|vue\?vue|ts|tsx|js|jsx|html)$/, /frontend\/src\/.*/],
      exclude: [/node_modules/, /dist/, /coverage/],
    },
  },
})
