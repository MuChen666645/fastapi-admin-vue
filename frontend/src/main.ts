import { createApp } from 'vue'
import { createPinia } from 'pinia'
import '@unocss/reset/tailwind.css'
import 'virtual:uno.css'
// 通用字体
import 'vfonts/Lato.css'
import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.config.performance = import.meta.env.DEV

const bootstrap = async (): Promise<void> => {
  await router.isReady()
  app.mount('#app')
}

void bootstrap()
