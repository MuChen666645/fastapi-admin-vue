import { defineConfig, presetWind3 } from 'unocss'

export default defineConfig({
  presets: [presetWind3()],
  content: {
    pipeline: {
      include: [
        /\.(vue|vue\?vue|ts|tsx|js|jsx|html)$/,
        /frontend\/src\/.*/,
      ],
      exclude: [
        /node_modules/,
        /dist/,
        /coverage/,
      ],
    },
  },
})
