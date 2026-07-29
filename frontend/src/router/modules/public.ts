import type { RouteRecordRaw } from 'vue-router'

import LoginView from '@/views/login/index.vue'

export const publicRoutes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: {
      title: '鐧诲綍',
      menu: false,
      hideBreadcrumb: true,
      public: true,
    },
  },
]
