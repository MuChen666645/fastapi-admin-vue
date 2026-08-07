import { createApp } from 'vue'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'

import 'virtual:uno.css'
import 'vfonts/Lato.css'
import './assets/styles/fastapi-admin.scss'
import App from './App.vue'
import { permissionDirective } from './directives'
import router from './router'

const app = createApp(App)
const pinia = createPinia()

pinia.use(piniaPluginPersistedstate)

app.use(pinia)
app.use(router)
app.directive('permission', permissionDirective)
app.config.performance = import.meta.env.DEV

app.mount('#app')
